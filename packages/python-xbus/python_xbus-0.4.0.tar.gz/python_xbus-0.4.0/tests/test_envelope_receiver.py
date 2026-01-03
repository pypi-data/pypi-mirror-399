import asyncio
import uuid

import pytest
from xbus import envelope_receiver, envelope_writer, xbus_pb2


@pytest.mark.asyncio
async def test_envelope_receive_1_fragment():
    sent = []

    async def append(x):
        sent.append(x)

    ew = envelope_writer.EnvelopeWriter(append, ["evt1", "evt2"])
    await ew.add_items("evt1", b"it1", b"it2")
    await ew.add_items("evt2", b"it3", b"it4")
    await ew.close()

    assert len(sent) == 1
    print(sent)

    fragment = sent[0]
    assert fragment is not None

    er = envelope_receiver.EnvelopeReceiver("default")
    await er.receive(fragment)

    assert list(er._messages.values())[0].complete
    assert er.is_complete()

    envelope = await er.complete(1.0)

    assert envelope is not None
    assert envelope.id == fragment.id


@pytest.mark.asyncio
async def test_envelope_receive_complete_timeout():
    er = envelope_receiver.EnvelopeReceiver("default")

    try:
        await er.complete(0.1)
        assert False
    except asyncio.exceptions.TimeoutError:
        pass


@pytest.mark.asyncio
async def test_envelope_receive_multiple_fragments(splitted_envelope_1):
    er = envelope_receiver.EnvelopeReceiver("default", splitted_envelope_1[0])
    assert not er._messages[splitted_envelope_1[0].eventIDs[0]].done
    assert not er._messages[splitted_envelope_1[0].eventIDs[1]].done

    for f in splitted_envelope_1[1:]:
        await er.receive(f)

    assert (
        er._messages[splitted_envelope_1[0].eventIDs[0]].current_itemcount == 1
    )
    assert (
        er._messages[splitted_envelope_1[0].eventIDs[0]].event.itemCount == 1
    )
    assert (
        er._messages[splitted_envelope_1[0].eventIDs[1]].current_itemcount == 2
    )
    assert (
        er._messages[splitted_envelope_1[0].eventIDs[1]].event.itemCount == 2
    )
    assert er._messages[splitted_envelope_1[0].eventIDs[0]].complete
    assert er._messages[splitted_envelope_1[0].eventIDs[1]].complete

    ev = await er.complete()

    assert len(ev.eventIDs) == 2
    assert len(ev.events) == 2
    assert ev.events[0].items == [b"item1"]
    assert ev.events[1].items == [b"item1", b"item2"]


@pytest.fixture
def splitted_envelope_1():
    fragments = []

    e = xbus_pb2.Envelope()
    e.id = uuid.UUID(hex="a12d893e-e1ae-11e6-aef5-339560dfd43a").bytes
    e.eventIDs.extend(
        [
            uuid.UUID(hex="dde084da-e1ae-11e6-a3de-67c62b00c0ec").bytes,
            uuid.UUID(hex="e9bff948-e1ae-11e6-81f5-0ff0cdd2468f").bytes,
        ]
    )

    ev = e.events.add()
    ev.id = uuid.UUID(hex="dde084da-e1ae-11e6-a3de-67c62b00c0ec").bytes
    ev.type = "evt1"
    ev.index = 1

    ev = e.events.add()
    ev.id = uuid.UUID("e9bff948-e1ae-11e6-81f5-0ff0cdd2468f").bytes
    ev.type = "evt2"
    ev.index = 1

    fragments.append(e)

    e = xbus_pb2.Envelope()
    e.id = uuid.UUID(hex="a12d893e-e1ae-11e6-aef5-339560dfd43a").bytes

    ev = e.events.add()
    ev.id = uuid.UUID(hex="dde084da-e1ae-11e6-a3de-67c62b00c0ec").bytes
    ev.index = 2
    ev.items[:] = [b"item1"]

    ev = e.events.add()
    ev.id = uuid.UUID("e9bff948-e1ae-11e6-81f5-0ff0cdd2468f").bytes
    ev.index = 2
    ev.items[:] = [b"item1"]

    fragments.append(e)

    e = xbus_pb2.Envelope()
    e.id = uuid.UUID(hex="a12d893e-e1ae-11e6-aef5-339560dfd43a").bytes

    ev = e.events.add()
    ev.id = uuid.UUID("e9bff948-e1ae-11e6-81f5-0ff0cdd2468f").bytes
    ev.index = 3
    ev.items[:] = [b"item2"]

    fragments.append(e)

    e = xbus_pb2.Envelope()
    e.id = uuid.UUID(hex="a12d893e-e1ae-11e6-aef5-339560dfd43a").bytes

    ev = e.events.add()
    ev.id = uuid.UUID("dde084da-e1ae-11e6-a3de-67c62b00c0ec").bytes
    ev.index = 3
    ev.itemCount = 1
    ev.checksum = 0xFD7F39FF

    ev = e.events.add()
    ev.id = uuid.UUID("e9bff948-e1ae-11e6-81f5-0ff0cdd2468f").bytes
    ev.index = 4
    ev.itemCount = 2
    ev.checksum = 0x54F8919C

    fragments.append(e)

    print("fragments", fragments)
    return fragments
