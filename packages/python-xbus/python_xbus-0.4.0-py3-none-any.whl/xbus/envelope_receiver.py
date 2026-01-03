import asyncio
import logging
import uuid
from typing import AsyncIterator, Optional

from . import checksum
from . import xbus_pb2 as api

log = logging.getLogger(__name__)


class ChecksumError(RuntimeError):
    def __init__(self, expected, actual):
        super().__init__(
            "invalid checksum. Expected %x, got %x" % (expected, actual)
        )


class IndexError(RuntimeError):
    pass


class MessageReceiver:
    def __init__(self, event):
        self.event = event
        self.current = None
        self.complete = False
        self.done = False
        self.queue = asyncio.Queue()
        self.current_checksum = checksum.Checksum(
            event.id + event.type.encode("ascii")
        )
        self.current_itemcount = 0
        self.current_index = 0

    def id(self):
        return uuid.UUID(bytes=self.event.id)

    def msgtype(self):
        return self.event.type

    def checksum(self):
        return self.event.checksum

    def itemcount(self):
        return self.event.itemCount

    def __aiter__(self):
        return self

    async def __anext__(self):
        chunk = await self.read_chunk()
        if chunk is None:
            raise StopAsyncIteration
        return chunk

    async def read_chunk(self):
        if self.done:
            return None
        if self.current:
            chunk = self.current
            self.current = None
            return chunk
        chunk = await self.queue.get()
        if chunk is None:
            self.done = True
        return chunk

    async def read(self, size=0):
        if self.done:
            raise EOFError()
        data = self.current or b""
        self.current = None
        while True:
            if size > 0 and len(data) >= size:
                self.current = data[size:]
                return data[:size]
            chunk = await self.queue.get()
            if chunk is None:
                self.done = True
                return data
            data += chunk

    def absorb(self, event):
        self.current_index += 1

        if self.current_index != event.index:
            raise IndexError()

        if event.checksum != 0:
            self.event.checksum = event.checksum
        if event.itemCount != 0:
            self.event.itemCount = event.itemCount

        for chunk in event.items:
            self.current_itemcount += 1
            self.current_checksum.update(chunk)
            self.queue.put_nowait(chunk)

        if (
            self.event.itemCount != 0
            and self.current_itemcount == self.event.itemCount
        ):
            self.complete = True
            if self.current_checksum.final() != self.event.checksum:
                raise ChecksumError(
                    self.event.checksum, self.current_checksum.final()
                )
            self.queue.put_nowait(None)


class EnvelopeReceiver(object):
    def __init__(self, inputname, fragment: Optional[api.Envelope] = None):
        self.inputname = inputname
        self.cond = asyncio.Condition()
        self.task = None

        self.id = None

        self._message_queue: asyncio.Queue | None = asyncio.Queue()
        self._messages = {}

        self._eventIDs = None

        if fragment:
            self.absorb_fragment(fragment)

    async def messages(self) -> AsyncIterator[MessageReceiver]:
        if self._message_queue is None:
            raise EOFError()
        while True:
            msg = await self._message_queue.get()
            if msg is None:
                self._message_queue = None
                break
            yield msg

    @property
    def reception_status(self):
        if self.is_complete():
            return api.EnvelopeAck.ACCEPTED

        return api.EnvelopeAck.RECEIVING

    def is_complete(self):
        return (
            (self._eventIDs or False)
            and set(self._messages.keys()) == set(self._eventIDs)
            and all(m.complete for m in self._messages.values())
        )

    def absorb_fragment(self, fragment: api.Envelope):
        if self.id is None:
            self.id = fragment.id
        else:
            assert self.id == fragment.id
        if fragment.eventIDs:
            self._eventIDs = list(fragment.eventIDs)
        for event in fragment.events:
            if event.id not in self._messages:
                # it's a new message!
                receiver = MessageReceiver(event)
                self._messages[event.id] = receiver
                if self._message_queue:
                    self._message_queue.put_nowait(receiver)
            else:
                receiver = self._messages[event.id]

            receiver.absorb(event)

        if self._eventIDs and set(self._messages.keys()) == set(
            self._eventIDs
        ):
            if self._message_queue:
                self._message_queue.put_nowait(None)

    async def receive(self, fragment):
        self.absorb_fragment(fragment)

    async def _complete(self):
        envelope = api.Envelope()

        async for msg in self.messages():
            ev = envelope.events.add()
            ev.id = msg.id().bytes
            ev.type = msg.msgtype()
            envelope.eventIDs.append(ev.id)

            async for item in msg:
                ev.items.append(item)

            ev.checksum = msg.checksum()
            ev.itemCount = msg.itemcount()
            ev.index = 1

        if self.id is not None:
            envelope.id = self.id

        return envelope

    async def complete(self, timeout=1):
        return await asyncio.wait_for(self._complete(), timeout)
