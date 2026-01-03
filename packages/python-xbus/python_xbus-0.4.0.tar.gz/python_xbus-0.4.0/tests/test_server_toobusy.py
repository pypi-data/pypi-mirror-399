import asyncio
import logging
import os

import nrpc.exc
import pytest
import xbus.fullenv
import xbus.service

log = logging.getLogger(__name__)

testdir = os.path.dirname(__file__)


class BusyConsumer:
    def __init__(self):
        self.instanciated = False

    def __call__(self, actor):
        print("Instanciating BusyConsumer")
        if self.instanciated:
            raise RuntimeError("Cannot have 2 BusyConsumer")

        self.instanciated = True
        self.cond = asyncio.Condition()
        self.attempts = 0
        self.complete = False

        return self

    async def process(self, apc):
        self.attempts += 1

        if self.attempts < 2:
            print("raising TOO BUSY")
            raise nrpc.exc.ServerTooBusy("too busy !")

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


@pytest.fixture
def busyconsumer():
    receiver = BusyConsumer()

    with xbus.service.temp_register("test.busyconsumer", receiver):
        yield receiver


@pytest.mark.asyncio
async def test_server_toobusy(busyconsumer):
    env = xbus.fullenv.Fullenv(
        os.path.join(testdir, "test_server_toobusy.yaml"),
    )

    async with env, env.up(), await env.load_client("inclient") as client:
        log.info(await env.wd())
        out = client.get_actor("emitter-1").open_output("default", ["demo.msg"])
        await out.add_items("demo.msg", b"hello world")
        await out.close()

        await busyconsumer.wait_for_completion(5)

        await asyncio.sleep(1)
