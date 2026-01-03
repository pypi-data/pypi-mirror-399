import itertools

import pytest
from xbus import envelope_writer

ALPHABET = b"abcdefghijklmnopqrstuvwxyz"


@pytest.mark.asyncio
async def test_envelope_write_1_fragment():
    sent = []

    async def append(x):
        sent.append(x)

    ew = envelope_writer.EnvelopeWriter(append)

    msg1 = ew.open_message("msg1")
    msg2 = ew.open_message("msg2")

    await ew.last_message()

    await msg1.write_chunk(b"it1")
    await msg1.write_chunk(b"it2")

    await msg2.write_chunk(b"it3")
    await msg2.write_chunk(b"it4")

    await msg1.close()
    await msg2.close()

    assert len(sent) == 1

    fragment = sent[0]

    assert fragment.id == ew.envelope.id
    assert fragment.events[0].type == "msg1"
    assert fragment.events[0].index == 1
    assert fragment.events[0].items == [b"it1", b"it2"]
    assert fragment.events[1].type == "msg2"
    assert fragment.events[1].index == 1
    assert fragment.events[1].items == [b"it3", b"it4"]


@pytest.mark.asyncio
async def test_envelope_write_big_message():
    sent = []

    async def append(x):
        sent.append(x)

    ew = envelope_writer.EnvelopeWriter(append)
    ew.MAX_SIZE = 50

    msg1 = ew.open_message("msg1")
    msg1.MAX_CHUNK_SIZE = 5

    await msg1.write_chunk(b"{}")
    await msg1.write(ALPHABET)
    await msg1.close()

    await ew.last_message()

    assert len(sent) == 6

    items = list(
        itertools.chain.from_iterable(
            f.events[0].items if f.events else [] for f in sent
        )
    )
    print(items)

    assert items[0] == b"{}"
    assert b"".join(items[1:]) == ALPHABET
