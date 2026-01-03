class PrintToConsole(object):
    def __init__(self, actor):
        self.actor = actor

    async def process(self, apc):
        envelope = await apc.envelope_complete("default")
        print("print-to-console:", envelope.events[0].items[0])
