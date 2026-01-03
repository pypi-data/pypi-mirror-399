import asyncio
import logging
import os

import pytest

import xbus.fullenv
import xbus.service

log = logging.getLogger(__name__)

testdir = os.path.dirname(__file__)


class CounterReceiver:
    def __init__(self):
        self.instanciated = False

    def __call__(self, actor):
        if self.instanciated:
            raise RuntimeError("Cannot have 2 CounterReceiver")

        self.instanciated = True

        self.offset = actor.settings.get_int("offset", 0)
        self.limit = actor.settings.get_int("limit", 10)
        self.missing_numbers = {}
        self.extra_numbers = {}

        self.next_expected = 0
        self.complete = False
        self.cond = asyncio.Condition()

        return self

    async def process(self, apc):
        envelope = await apc.read_envelope_complete("default", 1)
        n = int(envelope.events[0].items[0])

        await apc.log_warning("a little warning")

        if n < self.offset or n > self.limit:
            self.extra_numbers.add(n)
        elif n > self.next_expected:
            for i in range(self.next_expected, n):
                self.missing_numbers.add(i)
            self.next_expected = n + 1
        elif n < self.next_expected:
            del self.missing_numbers[n]
        else:
            self.next_expected += 1
        if self.next_expected > self.limit and not self.missing_numbers:
            async with self.cond:
                self.complete = True
                self.cond.notify_all()

    async def wait_for_completion(self, timeout):
        if not self.instanciated:
            raise RuntimeError("Need to be instanciated first")

        await self.cond.acquire()
        try:
            await asyncio.wait_for(
                self.cond.wait_for(lambda: self.complete), timeout=timeout
            )
        finally:
            if self.cond.locked():
                self.cond.release()


class run:
    def __init__(self, instance):
        self.instance = instance

    async def __aenter__(self):
        await self.instance.startup()
        return self.instance

    async def __aexit__(self, exc_type, exc, tb):
        await self.instance.shutdown()


class run_client:
    def __init__(self, client):
        self.client = client

    async def __aenter__(self):
        await self.client.connect()
        await self.client.startup()
        return self.client

    async def __aexit__(self, exc_type, exc, tb):
        await self.client.shutdown()


@pytest.fixture
def receivecounter():
    receiver = CounterReceiver()

    with xbus.service.temp_register("test.receivecounter", receiver):
        yield receiver


@pytest.mark.asyncio
async def test_counter_relay(receivecounter):
    env = xbus.fullenv.Fullenv(
        os.path.join(testdir, "test_fullenv_basics_counter_relay.yaml"),
    )

    async with env, env.up(), await env.load_client("inclient"):
        log.info(await env.wd())

        await receivecounter.wait_for_completion(30)

        await asyncio.sleep(1)

        output = (await env.ctl("ps", "export", "--all", "--full")).decode("utf-8")

        assert "a little warning" in output


@pytest.mark.asyncio
async def test_no_reconnect(receivecounter):
    env = xbus.fullenv.Fullenv(
        os.path.join(testdir, "test_fullenv_basics_counter_relay.yaml"),
    )

    stop_event = asyncio.Event()

    async def STOP():
        stop_event.set()

    async with env:
        filename, clientconf = await env.load_client_config("inclient")

        client = xbus.client.Client(
            clientconf,
            os.path.dirname(filename),
            no_reconnect=True,
        )

        await env.startup()
        await client.connect(stop=STOP)
        await asyncio.sleep(1)

    await asyncio.wait_for(stop_event.wait(), 1)
