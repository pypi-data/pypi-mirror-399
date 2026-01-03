# utilities to setup a full testing environment.

import asyncio
import os.path
import sys
from asyncio import subprocess

import yaml

import xbus.client
import xbus.service

from .actor_processing_context import ActorProcessingContext


class Error(RuntimeError):
    pass


class TestConsumer:
    def __init__(self, actor):
        self.inputs = {}

    async def process(self, apc: ActorProcessingContext):
        for i in apc.request.inputs:
            self.inputs[i.name] = await apc.read_envelope_complete(i.name, 240)


class FullenvRunContext:
    def __init__(self, env):
        self.env = env

    async def __aenter__(self):
        await self.env.startup()

    async def __aexit__(self, exc_type, exc, tb):
        await self.env.shutdown()


class Fullenv:
    def __init__(self, config):
        self.config = config
        self.process: asyncio.subprocess.Process | None = None
        self.consumers = {}

    def consumer_factory(self, actor):
        c = TestConsumer(actor)
        self.consumers[actor.name] = c
        return c

    async def _read_stderr(self):
        if not self.process or not self.process.stderr:
            raise RuntimeError("no process stderr to read")

        while True:
            line = await self.process.stderr.readline()
            if not line:
                return
            sys.stderr.buffer.write(line)

    async def _next_output(self):
        if not self.process or not self.process.stdout:
            raise RuntimeError("no process stdout to read")

        while True:
            line = await self.process.stdout.readline()
            if not line:
                # wait a little so stderr is properly flushed
                # TODO wait until _read_stderr is done?
                await asyncio.sleep(0.1)
                raise Error("Unexpected EOF")
            line = line.decode("utf-8").strip("\n")
            if not line.startswith("< "):
                continue
            if line.startswith("< OK: "):
                return line[6:]
            if line == "< OK":
                return None
            if line.startswith("< ERR: "):
                raise Error(line[7:])
            raise Error("Unexpected reply: %s" % line)

    async def _run_command(self, *args):
        if not self.process or not self.process.stdin:
            raise RuntimeError("no process stdin to write to")

        cmd = " ".join(args) + "\n"
        self.process.stdin.write(cmd.encode("utf-8"))
        await self.process.stdin.drain()
        return await self._next_output()

    async def init(self):
        if "XBUS_TEST_POSTGRES_DSN" not in os.environ:
            raise RuntimeError(
                "XBUS_TEST_POSTGRES_DSN must be defined to run fullenv tests"
            )
        xbus.service.register("fullenv.consumer", self.consumer_factory)
        self.process = await asyncio.create_subprocess_exec(
            "xbus-fullenv",
            "run",
            "--no-prompt",
            self.config,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        _ = asyncio.ensure_future(self._read_stderr())
        self.workdir = await self._next_output()

    async def close(self):
        try:
            await self._run_command("quit")
        except Exception:
            pass
        if self.process:
            await self.process.wait()
            self.process = None
        xbus.service.unregister("fullenv.consumer")

    async def __aenter__(self):
        await self.init()

    async def __aexit__(self, exc_type, exc, tb):
        await self.close()

    async def startup(self):
        await self._run_command("startup")

    async def shutdown(self):
        await self._run_command("shutdown")

    def up(self):
        return FullenvRunContext(self)

    async def client_config(self, clientname):
        return await self._run_command("client-config", clientname)

    def ctl_config(self):
        return os.path.join(self.workdir, "ctl", "xbusctl.yaml")

    async def wd(self):
        return await self._run_command("wd")

    async def load_client_config(self, clientname):
        filename = await self.client_config(clientname)
        confdict = yaml.load(open(filename, "rb"), Loader=yaml.Loader)

        return (filename, confdict)

    async def load_client(self, clientname):
        filename, confdict = await self.load_client_config(clientname)

        return xbus.client.Client(
            confdict,
            os.path.dirname(filename),
        )

    async def ctl(self, *cmd):
        p = await asyncio.create_subprocess_exec(
            "xbusctl",
            "--config",
            self.ctl_config(),
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await p.communicate()
        if len(stderr) != 0:
            raise RuntimeError(str(stderr))

        return stdout
