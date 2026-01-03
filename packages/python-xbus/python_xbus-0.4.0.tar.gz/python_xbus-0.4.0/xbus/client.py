import asyncio
import contextlib
import logging
import os
import ssl
import tempfile
import uuid

import nrpc.exc
import yaml
from nats.aio.client import Client as NATS
import nats.errors

from . import conn, envelope_writer, service, xbus_nrpc, xbus_pb2
from .actor_processing_context import ActorProcessingContext

log = logging.getLogger(__name__)


@contextlib.contextmanager
def pemfiles(*pem):
    tempfiles = []
    files = []
    for data in pem:
        if os.path.exists(data):
            files.append(data)
        else:
            f = tempfile.NamedTemporaryFile(delete=False)
            f.write(data.encode("ascii"))
            f.close()
            tempfiles.append(f.name)
            files.append(f.name)

    yield files

    for f in tempfiles:
        os.unlink(f)


class Settings(dict):
    def __init__(self, d):
        self.update(d)

    def get_int(self, key, default):
        if key in self:
            return int(self[key])
        return default


def init_actor_processing_state(context):
    state = xbus_pb2.ActorProcessingState()
    state.context.CopyFrom(context)
    state.status = xbus_pb2.ActorProcessingState.RUNNING
    return state


def actor_processing_state_log(state, level, msg):
    logm = state.messages.add()
    logm.time.GetCurrentTime()
    logm.level = level
    logm.Text = msg
    return state


def make_actor_processing_state(context, status, msg=None):
    state = xbus_pb2.ActorProcessingState()
    state.context.CopyFrom(context)
    state.status = status
    if msg is not None:
        logm = state.messages.add()
        logm.time.GetCurrentTime()
        logm.level = xbus_pb2.ERROR
        logm.Text = msg
        log.error(msg)
    return state


class ActorAgentServer:
    def __init__(self, actor, process_handler):
        self.conn = actor.client.clientconn()
        self.actor = actor
        self.process_handler = process_handler

    async def Process(self, request):
        apc = ActorProcessingContext(self.actor, request)

        apc.log_queue = asyncio.Queue(1)
        try:
            process_task = asyncio.create_task(self.process_handler(apc))
            get_log_task = asyncio.create_task(apc.log_queue.get())

            while True:
                done, _ = await asyncio.wait(
                    {process_task, get_log_task},
                    return_when=asyncio.FIRST_COMPLETED,
                )

                state = init_actor_processing_state(request.context)

                if get_log_task in done:
                    assert not apc.detached
                    (level, msg) = get_log_task.result()
                    actor_processing_state_log(state, level, msg)
                    if process_task not in done:
                        yield state
                        get_log_task = asyncio.create_task(apc.log_queue.get())
                        continue

                if process_task in done:
                    if not get_log_task.done():
                        get_log_task.cancel()
                    if not apc.detached:
                        if apc.err:
                            state.status = xbus_pb2.ActorProcessingState.ERROR
                            actor_processing_state_log(
                                state, xbus_pb2.ERROR, str(apc.error)
                            )
                        else:
                            exc = process_task.exception()
                            if exc is not None:
                                raise exc
                            state.status = (
                                xbus_pb2.ActorProcessingState.SUCCESS
                            )

                        yield state
                    break

        except nrpc.exc.NrpcError as e:
            raise e
        except Exception as e:
            log.exception("Error calling process")
            yield make_actor_processing_state(
                request.context, xbus_pb2.ActorProcessingState.ERROR, str(e)
            )


class Subscription:
    def __init__(self, conn, actor, sub):
        self.conn = conn
        self.actor = actor
        self.sub = sub

    async def unsubscribe(self):
        try:
            await xbus_nrpc.SentinelClient(self.conn).ActorLeaving(
                self.actor.id
            )
        finally:
            await self.sub.unsubscribe()


class Actor(object):
    def __init__(self, client, conf):
        self.client = client
        self.id = conf.get("id")
        self.name = conf["name"]
        self.kind = conf["kind"]
        self.roles = conf.get("roles")

        self.service = None

        serviceConf = conf.get("service", {})

        if serviceConf.get("type"):
            log.info("Instanciate service")
            self.service_type = serviceConf["type"]
            self.settings = Settings(serviceConf.get("settings", {}))

            self.service = service.load(self.service_type, self)
            log.info("service: %s", self.service)

    @property
    def broker(self):
        return xbus_nrpc.BrokerClient(self.client.clientconn(), self.id)

    @property
    def director(self):
        return xbus_nrpc.DirectorClient(self.client.clientconn())

    def open_output(self, output, eventtypes, context=None):
        async def send(fragment):
            req = xbus_pb2.OutputRequest(
                context=context, output=output, envelope=fragment
            )
            await self.broker.Output(req)

        return envelope_writer.EnvelopeWriter(send, eventtypes)

    async def forward_envelope(self, context, output, envelopeid):
        req = xbus_pb2.OutputRequest(
            context=context,
            output=output,
            envelope=xbus_pb2.Envelope(id=envelopeid, last=True),
        )
        await self.broker.Output(req)

    async def subscribe(self, process_handler):
        actor_agent_handler = xbus_nrpc.ActorAgentHandler(
            self.client.clientconn(), ActorAgentServer(self, process_handler)
        )
        subject = actor_agent_handler.subject(svc_actorID=str(self.id))
        conn = self.client.clientconn()
        sub = await conn.subscribe(subject, cb=actor_agent_handler.handler)
        sub = Subscription(conn, self, sub)
        try:
            await xbus_nrpc.SentinelClient(conn).ActorReady(self.id)
        except Exception:
            await sub.conn.unsubscribe(sub.sub.id)
            raise
        return sub

    async def processing_success(self, context):
        await self.processing_end(
            context, xbus_pb2.ActorProcessingState.SUCCESS
        )

    async def processing_error(self, context, envelope_id, msg):
        await self.processing_end(
            context, xbus_pb2.ActorProcessingState.ERROR, msg
        )

    async def processing_end(self, context, status, msg=None):
        req = xbus_pb2.ActorProcessingState()
        req.context.CopyFrom(context)
        req.status = status
        if msg is not None:
            logm = req.messages.add()
            logm.time.GetCurrentTime()
            logm.level = xbus_pb2.ERROR
            logm.Text = msg
            log.error(logm.Text)
        await self.director.ProcessingEnd(self.id, req)


class ClientConf(object):
    def __init__(self, d):
        self.d = d

    def _get(self, key, default=None):
        d = self.d
        if key in d:
            return d[key]
        for k in key.split("."):
            if k not in d:
                return default
            d = d[k]
        return d

    def _set(self, key, value):
        d = self.d
        if key in d:
            d[key] = value
            return
        path = key.split(".")
        for k in path[:-1]:
            if k not in d:
                d[k] = {}
            d = d[k]
        d[path[-1]] = value

    def __getitem__(self, key):
        return self._get(key, None)

    def __setitem__(self, key, value):
        return self._set(key, value)

    def listactors(self):
        actor_dict = self._get("actors", [])
        actors = []
        for key, value in actor_dict.items():
            try:
                int(key)
            except ValueError:
                name = value.get("name", key)
                if name != key:
                    raise ValueError(
                        "Inconsistent key/name: Key=%s, name=%s" % (key, name)
                    )
                value["name"] = name
            if "name" not in value:
                raise ValueError("Actor has no name: %s" % value)
            actors.append(value)
        return actors


class Client(object):
    def __init__(self, confdict=None, confdir=None, no_reconnect=False):
        if confdict is not None:
            self.load_conf(confdict, confdir)
        if no_reconnect:
            self.no_reconnect = True
        self.nc = None

    def load_conf(self, confdict, confdir):
        self.conf = ClientConf(confdict)
        self.no_reconnect = self.conf._get("no-reconnect", False)
        self.load_tls_conf(confdir)

        self.actors = [Actor(self, conf) for conf in self.conf.listactors()]

    def load_tls_conf(self, confdir):
        if confdir is None:
            confdir = os.getcwd()

        conf = self.conf

        name = conf["account-name"]

        if conf["tls.certdir"] is None and conf["tls.certfile"] is None:
            if name is not None:
                # we can forge a certfile path
                conf["tls.certfile"] = os.path.join(confdir, name + ".certs")

        if conf["tls.certdir"] and name:
            if (
                conf["tls.private-key"] is None
                and conf["tls.private-key-file"] is None
            ):
                conf["tls.private-key-file"] = os.path.join(
                    conf["tls.certdir"], name + ".key"
                )
            if (
                conf["tls.certificate"] is None
                and conf["tls.certificate-file"] is None
            ):
                conf["tls.certificate-file"] = os.path.join(
                    conf["tls.certdir"], name + ".crt"
                )
            if conf["tls.csr"] is None and conf["tls.csr-file"] is None:
                conf["tls.csr-file"] = os.path.join(
                    conf["tls.certdir"], name + ".csr"
                )
            if conf["tls.rootca"] is None and conf["tls.rootca-file"] is None:
                conf["tls.rootca-file"] = os.path.join("rootca.crt")

        certfile = {}
        if conf["tls.certfile"]:
            try:
                with open(conf["tls.certfile"]) as f:
                    certfile = yaml.load(f, Loader=yaml.Loader)
            except Exception:
                print("Could not load %s" % conf["tls.certfile"])
                certfile = {}  # handle old config style

        for entry in (
            "tls.private-key",
            "tls.certificate",
            "tls.csr",
            "tls.rootca",
        ):
            if conf[entry] is None:
                # attempt to load from a file if applicable
                if conf[entry + "-file"] is not None:
                    with open(conf[entry + "-file"]) as f:
                        conf[entry] = f.read()

                # check if present in the certfile
                if not conf[entry] and certfile.get(entry):
                    conf[entry] = certfile[entry]
                if not conf[entry]:
                    raise ValueError("Cannot load: {}".format(entry))

    def clientconn(self):
        return conn.ClientConn(self.nc, self.conf["account-id"])

    def get_actor(self, name):
        for actor in self.actors:
            if actor.name == name:
                return actor
        return None

    def on_error(self, stop):
        async def on_error(e):
            log.error(e)

            # workaround for https://github.com/nats-io/nats.py/issues/806
            if isinstance(e, nats.errors.UnexpectedEOF):
                await stop()

        return on_error

    def on_disconnected(self, stop):
        if self.no_reconnect and stop is not None:
            return stop

    async def connect(self, stop=None):
        ssl_ctx = ssl.SSLContext(protocol=ssl.PROTOCOL_TLS_CLIENT)
        ssl_ctx.load_verify_locations(cadata=self.conf["tls.rootca"])
        with pemfiles(
            self.conf["tls.certificate"], self.conf["tls.private-key"]
        ) as (
            certfile,
            keyfile,
        ):
            ssl_ctx.load_cert_chain(certfile=certfile, keyfile=keyfile)

        self.nc = NATS()
        servers = [self.conf["nats-url"] or "nats://localhost:4222"]
        await self.nc.connect(
            name="@3.0",
            servers=servers,
            error_cb=self.on_error(stop),
            disconnected_cb=self.on_disconnected(stop),
            tls=ssl_ctx,
            allow_reconnect=not self.no_reconnect,
        )

        await self.whoami()

        await self.load_actor_defs()

    async def whoami(self):
        whoami_client = xbus_nrpc.WhoAmIClient(
            conn.FixedInboxConn(
                self.nc,
                "xbus.default.client.whoami.%s.reply"
                % self.conf["account-name"],
            )
        )
        account = await whoami_client.WhoAmI(self.conf["account-name"])

        # TODO the account.id field should already be a UUID instance.
        # We need to customize the protobuf types
        self.conf["account-id"] = str(uuid.UUID(bytes=account.id))

    async def load_actor_defs(self):
        clientapi = xbus_nrpc.ClientAPIClient(
            self.clientconn(), self.conf["account-id"]
        )
        rep = await clientapi.GetActors()
        for actordef in rep.actors:
            actor = self.get_actor(actordef.name)
            if actor is None:
                continue
            actor.id = str(uuid.UUID(bytes=actordef.id))

    async def __aenter__(self):
        await self.connect()
        await self.startup()
        return self

    async def __aexit__(self, exc_type, exc, tb):
        await self.shutdown()
        await self.close()

    async def startup(self):
        log.info("Starting up")
        if self.nc is None:
            raise RuntimeError("connect() must be called before startup()")

        for actor in self.actors:
            if actor.service:
                if hasattr(actor.service, "startup"):
                    await actor.service.startup()
                if hasattr(actor.service, "process"):
                    actor.service._sub = await actor.subscribe(
                        actor.service.process
                    )

    async def shutdown(self):
        log.info("Shutting down")

        for actor in reversed(self.actors):
            if actor.service:
                if hasattr(actor.service, "_sub"):
                    await actor.service._sub.unsubscribe()
                    del actor.service._sub
                if hasattr(actor.service, "shutdown"):
                    await actor.service.shutdown()

    async def close(self):
        if self.nc:
            await self.nc.close()
            self.nc = None
