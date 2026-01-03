import asyncio

from nats.aio.client import DEFAULT_INBOX_PREFIX as INBOX_PREFIX
from nats.aio.errors import ErrTimeout
from nats.nuid import NUID


def ClientConn(nc, accountID):
    return CustomInboxPrefixConn(
        nc, INBOX_PREFIX.decode() + "." + str(accountID) + ".in."
    )


class CustomInboxPrefixConn:
    "Wraps a nats.Client with custom inbox prefix request functions"

    def __init__(self, nc, prefix):
        self.nc = nc
        self.inbox_prefix = prefix
        self._nuid = NUID()

    def __getattr__(self, attr):
        return getattr(self.nc, attr)

    def next_inbox(self):
        return "".join([self.inbox_prefix, self._nuid.next().decode()])

    async def request(self, subject, payload, timeout=0.5):
        inbox = self.next_inbox()
        future = asyncio.Future()
        sub = await self.subscribe(inbox, future=future, max_msgs=1)
        await sub.unsubscribe(1)
        await self.publish(subject, payload, reply=inbox)

        try:
            msg = await asyncio.wait_for(future, timeout)
            return msg
        except asyncio.TimeoutError:
            future.cancel()
            raise ErrTimeout


class FixedInboxConn:
    def __init__(self, nc, inbox):
        self.nc = nc
        self.inbox = inbox

    def __getattr__(self, attr):
        return getattr(self.nc, attr)

    async def request(self, subject, payload, timeout=0.5):
        inbox = self.inbox
        future = asyncio.Future()
        sub = await self.subscribe(inbox, future=future, max_msgs=1)
        await sub.unsubscribe(1)
        await self.publish(subject, payload, reply=inbox)

        try:
            msg = await asyncio.wait_for(future, timeout)
            return msg
        except asyncio.TimeoutError:
            await sub.unsubscribe()
            future.cancel()
            raise ErrTimeout
