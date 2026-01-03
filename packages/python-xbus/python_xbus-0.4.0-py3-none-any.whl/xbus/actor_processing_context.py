import asyncio
import logging
from typing import List, Optional

from . import envelope_writer, xbus_nrpc, xbus_pb2
from .envelope_receiver import EnvelopeReceiver

log = logging.getLogger(__name__)


async def receive_envelope(conn, clientKind, clientID, position, receiver):
    async for fragmentAndPos in xbus_nrpc.EnvelopeStorageClient(conn).Retrieve(
        clientKind, clientID, position
    ):
        await receiver.receive(fragmentAndPos.fragment)


class ActorProcessingContext:
    def __init__(self, actor, request: xbus_pb2.ActorProcessRequest):
        self.conn = actor.client.clientconn()
        self.actor = actor
        self.request = request
        self._success = False
        self.detached = False
        self.log_queue = None
        self.err = None

    def detach(self):
        self.detached = True

    async def log(self, level, msg):
        if self.detached:
            raise RuntimeError("cannot log in a detached job")
        if self.log_queue is None:
            raise RuntimeError("no logging queue")
        await self.log_queue.put((level, msg))

    async def log_notice(self, msg):
        await self.log(xbus_pb2.NOTICE, msg)

    async def log_warning(self, msg):
        await self.log(xbus_pb2.WARNING, msg)

    async def log_error(self, msg):
        await self.log(xbus_pb2.ERROR, msg)

    async def success(self):
        self._success = True
        if self.detached:
            await self.actor.processing_success(self.request.context)

    async def error(self, err):
        self.err = err
        if self.detached:
            await self.actor.processing_end(self.request.context, str(err))

    def get_input(self, input_name):
        for input_ in self.request.inputs:
            if input_.name == input_name:
                return input_
        return None

    def read_envelope(self, input_name):
        for input_ in self.request.inputs:
            if input_.name == input_name:
                receiver = EnvelopeReceiver(input_name, input_.envelope)
                if receiver.reception_status == xbus_pb2.EnvelopeAck.RECEIVING:
                    receiver.task = asyncio.ensure_future(
                        receive_envelope(
                            self.conn,
                            "actor",
                            self.actor.id,
                            input_.position,
                            receiver,
                        )
                    )
                return receiver

    async def read_envelope_complete(self, input_name, timeout):
        er = self.read_envelope(input_name)
        return await er.complete(timeout)

    def open_output(self, output: str, eventtypes: Optional[List[str]] = None):
        async def send(fragment):
            req = xbus_pb2.OutputRequest(
                context=self.request.context, output=output, envelope=fragment
            )
            await self.actor.broker.Output(req)

        return envelope_writer.EnvelopeWriter(send, eventtypes)

    async def forward(self, output, input_name=None, envelopeid=None):
        if input_name is not None:
            input_ = self.get_input(input_name)
            if input_ is None:
                raise RuntimeError("no such input")
            envelopeid = input_.envelope.id
        await self.actor.forward_envelope(
            self.request.context, output, envelopeid
        )
