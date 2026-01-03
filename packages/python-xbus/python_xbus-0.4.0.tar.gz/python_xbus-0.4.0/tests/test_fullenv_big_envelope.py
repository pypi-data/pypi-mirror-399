import asyncio
import logging
import os

import pytest
import xbus.fullenv
import xbus.service

from test_envelope_writer_ng import ALPHABET

log = logging.getLogger(__name__)

testdir = os.path.dirname(__file__)

statuses = [b"RUNNING", b"ERROR", b"PAUSED", b"DONE"]


def ps_status(stdout):
    for status in statuses:
        if status in stdout:
            return status.decode("ascii")
    raise RuntimeError("could not find a status")


class Relay:
    def __init__(self, actor):
        pass

    async def relay_message(self, w, msg):
        async for chunk in msg:
            await w.write(chunk)
        await w.close()

    async def process(self, apc):
        e = apc.read_envelope("default")
        out = apc.open_output("default")
        log.info("relaying 'default'")
        async for msg in e.messages():
            log.info("relay: writing message %s", msg.msgtype())
            w = out.open_message(msg.msgtype())
            await self.relay_message(w, msg)
            log.info("relay: wrote message %s", msg.msgtype())
        await out.last_message()
        log.info("done relaying 'default'")


@pytest.fixture
def relay():
    with xbus.service.temp_register("test.relay", Relay):
        yield None


@pytest.mark.asyncio
async def test_big_envelope(relay):
    env = xbus.fullenv.Fullenv(
        os.path.join(testdir, "test_fullenv_big_envelope.yaml"),
    )

    async with env, env.up(), await env.load_client("inclient") as client:
        log.info(await env.wd())

        emitter = client.get_actor("emitter")
        assert emitter is not None

        ew = emitter.open_output("default", None)
        mw1 = ew.open_message("msg1")
        mw2 = ew.open_message("msg2")
        mw3 = ew.open_message("msg3")
        await ew.last_message()

        log.info("writing")
        for _ in range(1000):
            await mw1.write(ALPHABET * 100)
            await mw2.write(ALPHABET * 1000)
            await mw3.write(ALPHABET * 100)

        await mw1.close()
        await mw2.close()
        await mw3.close()

        log.info("wrote the envelope, now waiting")

        while True:
            await asyncio.sleep(1)
            status = ps_status(await env.ctl("ps", "--all"))
            log.info("process status: %s", status)
            if status != "RUNNING":
                break

        status = ps_status(await env.ctl("ps", "--all"))
        if status == "ERROR":
            print(
                (
                    await env.ctl(
                        "ps",
                        "export",
                        "--export-logs",
                        "--export-process-logs",
                        "--all",
                    )
                ).decode("utf-8")
            )
        assert status == "DONE"

        consumer = env.consumers["consumer"]
        assert len(consumer.inputs) == 1
        envelope = consumer.inputs["default"]
        assert len(envelope.events) == 3
        for e in envelope.events:
            if e.type == "msg2":
                assert sum(len(item) for item in e.items) == 26 * 1000 * 1000
            else:
                assert sum(len(item) for item in e.items) == 26 * 100 * 1000
