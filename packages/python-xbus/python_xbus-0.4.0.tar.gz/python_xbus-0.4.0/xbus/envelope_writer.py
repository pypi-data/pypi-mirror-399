import logging
import uuid
from typing import Awaitable, Callable, List, Optional, Tuple

from . import checksum, xbus_pb2

log = logging.getLogger(__name__)


class ChunkTooBigError(RuntimeError):
    pass


class MessageWriter:
    MAX_CHUNK_SIZE = 1024 * 100

    def __init__(
        self,
        write: Callable[[bytes], Awaitable[None]],
        close: Callable[[], Awaitable[None]],
    ):
        self._write = write
        self._close = close
        self.buffer = b""

    async def flush(self, complete=False):
        while self.buffer:
            if not complete and len(self.buffer) < self.MAX_CHUNK_SIZE:
                return
            size = min(len(self.buffer), self.MAX_CHUNK_SIZE)
            chunk = self.buffer[:size]
            self.buffer = self.buffer[size:]
            await self._write(chunk)

    async def write_chunk(self, data: bytes):
        if len(data) > self.MAX_CHUNK_SIZE:
            raise ChunkTooBigError
        await self._write(data)

    async def write(self, data):
        if not isinstance(data, bytes):
            raise RuntimeError("Expecting bytes, got: %s" % data)
        self.buffer += data
        await self.flush()

    async def close(self):
        await self.flush(True)
        await self._close()


class EnvelopeWriter:
    MAX_SIZE = 1024 * 500

    def __init__(
        self,
        send: Callable[[xbus_pb2.Envelope], Awaitable[None]],
        event_types: Optional[List[str]] = None,
    ):
        self._send = send
        self.envelope = xbus_pb2.Envelope()
        env_id = uuid.uuid4()
        self.envelope.id = env_id.bytes

        self.events = {}
        self.eventIDs = []
        self.checksums = {}
        self.closed_events = set()
        self.finalized_events = set()
        self.no_more_events = False

        self.pending_event_headers = []

        self.legacy_event_types = {}
        if event_types:
            for event_type in event_types:
                id = uuid.uuid4()
                self.legacy_event_types[event_type] = id
                self.add_event(id, event_type)
            self.no_more_events = True

    def open_message(self, msgtype: str) -> MessageWriter:
        id = uuid.uuid4()
        self.add_event(id, msgtype)

        return MessageWriter(
            write=lambda item: self.add_item(id, item),
            close=lambda: self.close_event(id),
        )

    async def last_message(self):
        await self.last_event()

    def add_event(self, id: uuid.UUID, msgtype: str):
        event = xbus_pb2.Event()
        event.id = id.bytes
        event.type = msgtype
        event.index = 1
        event.itemCount = 0

        self.checksums[id] = checksum.Checksum(
            id.bytes + msgtype.encode("ascii")
        )

        self.events[id] = event
        self.eventIDs.append(id)
        self.pending_event_headers.append(id)

    async def add_item(self, id: uuid.UUID, item: bytes):
        if len(item) > self.MAX_SIZE * 9 / 10:
            raise ChunkTooBigError()
        self.checksums[id].update(item)
        self.events[id].items.append(item)
        self.events[id].itemCount += 1
        await self.flush()

    async def add_items(self, eventType: str, *items: bytes):
        for item in items:
            await self.add_item(self.legacy_event_types[eventType], item)

    async def close_event(self, id: uuid.UUID):
        self.closed_events.add(id)
        await self.flush()

    async def last_event(self):
        self.no_more_events = True
        await self.flush()

    def size(self):
        return self.envelope.ByteSize() + sum(
            event.ByteSize() for event in self.events.values()
        )

    async def flush(self):
        while (
            self.size() > self.MAX_SIZE
            or self.no_more_events
            and len(self.closed_events) == len(self.events)
        ):
            envelope, is_last = self.build_next()
            await self._send(envelope)
            if is_last:
                break

    def build_next(self) -> Tuple[xbus_pb2.Envelope, bool]:
        envelope = xbus_pb2.Envelope()
        envelope.id = self.envelope.id

        if self.no_more_events:
            envelope.eventIDs[:] = [id.bytes for id in self.eventIDs]

        for id in self.eventIDs:
            event = self.events[id]
            if event.id in self.finalized_events:
                continue
            items = pop_items(event.items, self.MAX_SIZE - envelope.ByteSize())

            if (
                len(items) != 0
                or id in self.closed_events
                or id in self.pending_event_headers
            ):
                ev = envelope.events.add()
                ev.id = event.id
                ev.type = event.type
                ev.items[:] = items
                ev.index = event.index
                event.index += 1

                if id in self.closed_events:
                    ev.checksum = self.checksums[id].final()
                    ev.itemCount = event.itemCount

                    if len(items) == 0:
                        self.finalized_events.add(event.id)
                if id in self.pending_event_headers:
                    self.pending_event_headers.remove(id)

        all_events_closed = len(self.closed_events) == len(self.events)

        pending_items = sum(len(event.items) for event in self.events.values())

        is_last = (
            self.no_more_events and all_events_closed and (pending_items == 0)
        )

        return envelope, is_last

    async def close(self):
        for id in self.legacy_event_types.values():
            await self.close_event(id)


Items = List[bytes]


def pop_items(items: Items, maxsize: int) -> Items:
    size = 0
    i = 0
    while i < len(items) and size + len(items[i]) < maxsize:
        size += len(items[i])
        i += 1
    result = items[:i]
    items[:] = items[i:]
    return result
