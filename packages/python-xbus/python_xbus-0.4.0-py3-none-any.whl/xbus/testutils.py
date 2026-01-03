import asyncio

from . import client, envelope_writer, xbus_pb2
from .envelope_receiver import EnvelopeReceiver


class Actor:
    def __init__(self, id_, name, kind, roles, settings={}):
        self.client = None
        self.id = id_
        self.name = name
        self.kind = kind
        self.roles = roles
        self.settings = client.Settings(settings)


# build envelope fragments from [('eventtype', 'content' or [items])]
async def make_envelope(*messages):
    result = []

    async def send(fragment):
        nonlocal result
        result.append(fragment)

    writer = envelope_writer.EnvelopeWriter(send)
    for msgtype, content in messages:
        mw = writer.open_message(msgtype)

        if isinstance(content, list):
            for chunk in content:
                if hasattr(chunk, "read"):
                    data = chunk.read()
                    await mw.write(data)
                    await mw.flush(complete=True)
                else:
                    await mw.write_chunk(chunk)
        elif hasattr(content, "read"):
            await mw.write(content.read())
        else:
            await mw.write(content)

        await mw.close()

    await writer.last_message()

    return result


async def make_request(**inputs):
    r = xbus_pb2.ActorProcessRequest()
    tails = {}
    for inputname, envelope in inputs.items():
        in_ = r.inputs.add()
        in_.name = inputname
        if isinstance(envelope, tuple):
            envelope = await make_envelope(envelope)
        elif isinstance(envelope, list):
            if isinstance(envelope[0], tuple):
                envelope = await make_envelope(*envelope)
        in_.envelope.CopyFrom(envelope[0])
        tails[inputname] = envelope[1:]
    return r, tails


async def receive_envelope(fragments, receiver):
    for f in fragments:
        await receiver.receive(f)


class APC:
    def __init__(self, actor, request, tails={}):
        self.actor = actor
        self.request = request
        self.tails = tails
        self.outputs = {}
        self.forwarded = {}

    def detach(self):
        self._detached = True

    async def success(self):
        self._success = True

    async def error(self, err):
        self._error = err

    def read_envelope(self, input_name):
        for input_ in self.request.inputs:
            if input_.name == input_name:
                receiver = EnvelopeReceiver(input_name, input_.envelope)
                tail = self.tails.get(input_name, None)
                if tail:
                    receiver.task = asyncio.ensure_future(
                        receive_envelope(tail, receiver)
                    )
                return receiver

    async def read_envelope_complete(self, input_name, timeout):
        er = self.read_envelope(input_name)
        return await er.complete(timeout)

    def open_output(self, output, eventtypes=None):
        async def send(fragment):
            self.outputs.setdefault(output, []).append(fragment)

        return envelope_writer.EnvelopeWriter(send, eventtypes)

    async def forward(self, output, input_name=None, envelopeid=None):
        self.forwarded[output] = (input_name, envelopeid)
