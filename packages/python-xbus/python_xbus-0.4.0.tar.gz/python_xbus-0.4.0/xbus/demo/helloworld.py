import asyncio


class HelloWorld(object):
    def __init__(self, actor):
        self.actor = actor
        self.message = actor.settings.get("message", "Hello world")
        self.interval = actor.settings.get_int("interval", 1)
        self.task = None

    async def run(self):
        try:
            while True:
                output = self.actor.open_output(
                    output="default", eventtypes=["demo.simplemessage"]
                )
                await output.add_items(
                    "demo.simplemessage", self.message.encode("utf-8")
                )
                await output.close()
                await asyncio.sleep(self.interval)
        except Exception as e:
            print("Error in helloword", e)
            raise

    async def startup(self):
        self.task = asyncio.ensure_future(self.run())

    async def shutdown(self):
        if self.task:
            self.task.cancel()
            await asyncio.wait([self.task])
            if self.task.exception():
                raise self.task.exception()
            self.task = None
