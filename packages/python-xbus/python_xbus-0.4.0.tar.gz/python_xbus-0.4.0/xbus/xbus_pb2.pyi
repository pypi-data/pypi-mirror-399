from google.protobuf import timestamp_pb2 as _timestamp_pb2
from nrpc import nrpc_pb2 as _nrpc_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class LogLevel(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    NOTICE: _ClassVar[LogLevel]
    WARNING: _ClassVar[LogLevel]
    ERROR: _ClassVar[LogLevel]
NOTICE: LogLevel
WARNING: LogLevel
ERROR: LogLevel

class LogMessage(_message.Message):
    __slots__ = ("time", "level", "Text")
    TIME_FIELD_NUMBER: _ClassVar[int]
    LEVEL_FIELD_NUMBER: _ClassVar[int]
    TEXT_FIELD_NUMBER: _ClassVar[int]
    time: _timestamp_pb2.Timestamp
    level: LogLevel
    Text: str
    def __init__(self, time: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., level: _Optional[_Union[LogLevel, str]] = ..., Text: _Optional[str] = ...) -> None: ...

class ConfigEntry(_message.Message):
    __slots__ = ("key", "value")
    KEY_FIELD_NUMBER: _ClassVar[int]
    VALUE_FIELD_NUMBER: _ClassVar[int]
    key: str
    value: str
    def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...

class Account(_message.Message):
    __slots__ = ("id", "name", "description", "type", "status", "csr", "csrOrigin", "cert", "apiKey")
    class Status(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        NOSTATUS: _ClassVar[Account.Status]
        PENDING: _ClassVar[Account.Status]
        ENABLED: _ClassVar[Account.Status]
        DISABLED: _ClassVar[Account.Status]
    NOSTATUS: Account.Status
    PENDING: Account.Status
    ENABLED: Account.Status
    DISABLED: Account.Status
    class Type(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        NOTYPE: _ClassVar[Account.Type]
        ACTOR: _ClassVar[Account.Type]
        USER: _ClassVar[Account.Type]
        GATEWAY: _ClassVar[Account.Type]
    NOTYPE: Account.Type
    ACTOR: Account.Type
    USER: Account.Type
    GATEWAY: Account.Type
    class CSROrigin(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        ANONYMOUS: _ClassVar[Account.CSROrigin]
        AUTHACCOUNT: _ClassVar[Account.CSROrigin]
    ANONYMOUS: Account.CSROrigin
    AUTHACCOUNT: Account.CSROrigin
    ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    CSR_FIELD_NUMBER: _ClassVar[int]
    CSRORIGIN_FIELD_NUMBER: _ClassVar[int]
    CERT_FIELD_NUMBER: _ClassVar[int]
    APIKEY_FIELD_NUMBER: _ClassVar[int]
    id: bytes
    name: str
    description: str
    type: Account.Type
    status: Account.Status
    csr: str
    csrOrigin: Account.CSROrigin
    cert: str
    apiKey: str
    def __init__(self, id: _Optional[bytes] = ..., name: _Optional[str] = ..., description: _Optional[str] = ..., type: _Optional[_Union[Account.Type, str]] = ..., status: _Optional[_Union[Account.Status, str]] = ..., csr: _Optional[str] = ..., csrOrigin: _Optional[_Union[Account.CSROrigin, str]] = ..., cert: _Optional[str] = ..., apiKey: _Optional[str] = ...) -> None: ...

class Actor(_message.Message):
    __slots__ = ("id", "name", "description", "kind", "status", "accountID", "roles", "lastSeen", "online", "unresponsive", "config")
    class Kind(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        CONSUMER: _ClassVar[Actor.Kind]
        EMITTER: _ClassVar[Actor.Kind]
        WORKER: _ClassVar[Actor.Kind]
    CONSUMER: Actor.Kind
    EMITTER: Actor.Kind
    WORKER: Actor.Kind
    class Status(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        PENDING: _ClassVar[Actor.Status]
        ENABLED: _ClassVar[Actor.Status]
        DISABLED: _ClassVar[Actor.Status]
        REJECTED: _ClassVar[Actor.Status]
    PENDING: Actor.Status
    ENABLED: Actor.Status
    DISABLED: Actor.Status
    REJECTED: Actor.Status
    ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    KIND_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    ACCOUNTID_FIELD_NUMBER: _ClassVar[int]
    ROLES_FIELD_NUMBER: _ClassVar[int]
    LASTSEEN_FIELD_NUMBER: _ClassVar[int]
    ONLINE_FIELD_NUMBER: _ClassVar[int]
    UNRESPONSIVE_FIELD_NUMBER: _ClassVar[int]
    CONFIG_FIELD_NUMBER: _ClassVar[int]
    id: bytes
    name: str
    description: str
    kind: Actor.Kind
    status: Actor.Status
    accountID: bytes
    roles: _containers.RepeatedScalarFieldContainer[str]
    lastSeen: _timestamp_pb2.Timestamp
    online: bool
    unresponsive: bool
    config: _containers.RepeatedCompositeFieldContainer[ConfigEntry]
    def __init__(self, id: _Optional[bytes] = ..., name: _Optional[str] = ..., description: _Optional[str] = ..., kind: _Optional[_Union[Actor.Kind, str]] = ..., status: _Optional[_Union[Actor.Status, str]] = ..., accountID: _Optional[bytes] = ..., roles: _Optional[_Iterable[str]] = ..., lastSeen: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., online: bool = ..., unresponsive: bool = ..., config: _Optional[_Iterable[_Union[ConfigEntry, _Mapping]]] = ...) -> None: ...

class CoreEvent(_message.Message):
    __slots__ = ("name", "actor", "process", "processOldStatus")
    NAME_FIELD_NUMBER: _ClassVar[int]
    ACTOR_FIELD_NUMBER: _ClassVar[int]
    PROCESS_FIELD_NUMBER: _ClassVar[int]
    PROCESSOLDSTATUS_FIELD_NUMBER: _ClassVar[int]
    name: str
    actor: Actor
    process: Process
    processOldStatus: Process.Status
    def __init__(self, name: _Optional[str] = ..., actor: _Optional[_Union[Actor, _Mapping]] = ..., process: _Optional[_Union[Process, _Mapping]] = ..., processOldStatus: _Optional[_Union[Process.Status, str]] = ...) -> None: ...

class EnvelopeEvent(_message.Message):
    __slots__ = ("envelopeID", "status", "newData")
    class Status(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        UNKNOWN: _ClassVar[EnvelopeEvent.Status]
        RECEIVING: _ClassVar[EnvelopeEvent.Status]
        COMPLETE: _ClassVar[EnvelopeEvent.Status]
        ERROR: _ClassVar[EnvelopeEvent.Status]
        STALLED: _ClassVar[EnvelopeEvent.Status]
    UNKNOWN: EnvelopeEvent.Status
    RECEIVING: EnvelopeEvent.Status
    COMPLETE: EnvelopeEvent.Status
    ERROR: EnvelopeEvent.Status
    STALLED: EnvelopeEvent.Status
    ENVELOPEID_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    NEWDATA_FIELD_NUMBER: _ClassVar[int]
    envelopeID: bytes
    status: EnvelopeEvent.Status
    newData: bool
    def __init__(self, envelopeID: _Optional[bytes] = ..., status: _Optional[_Union[EnvelopeEvent.Status, str]] = ..., newData: bool = ...) -> None: ...

class ProcessNodeReadyEvent(_message.Message):
    __slots__ = ("processID", "actorID", "nodeID")
    PROCESSID_FIELD_NUMBER: _ClassVar[int]
    ACTORID_FIELD_NUMBER: _ClassVar[int]
    NODEID_FIELD_NUMBER: _ClassVar[int]
    processID: bytes
    actorID: bytes
    nodeID: str
    def __init__(self, processID: _Optional[bytes] = ..., actorID: _Optional[bytes] = ..., nodeID: _Optional[str] = ...) -> None: ...

class EmitterEnvelopeState(_message.Message):
    __slots__ = ("processID", "processCreatedAt", "status", "errors", "response", "triggerEnvelope")
    PROCESSID_FIELD_NUMBER: _ClassVar[int]
    PROCESSCREATEDAT_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    ERRORS_FIELD_NUMBER: _ClassVar[int]
    RESPONSE_FIELD_NUMBER: _ClassVar[int]
    TRIGGERENVELOPE_FIELD_NUMBER: _ClassVar[int]
    processID: bytes
    processCreatedAt: _timestamp_pb2.Timestamp
    status: Process.Status
    errors: _containers.RepeatedCompositeFieldContainer[LogMessage]
    response: EnvelopeFragmentAndPosition
    triggerEnvelope: EnvelopeFragmentAndPosition
    def __init__(self, processID: _Optional[bytes] = ..., processCreatedAt: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., status: _Optional[_Union[Process.Status, str]] = ..., errors: _Optional[_Iterable[_Union[LogMessage, _Mapping]]] = ..., response: _Optional[_Union[EnvelopeFragmentAndPosition, _Mapping]] = ..., triggerEnvelope: _Optional[_Union[EnvelopeFragmentAndPosition, _Mapping]] = ...) -> None: ...

class EmitterEnvelopeStateList(_message.Message):
    __slots__ = ("list",)
    LIST_FIELD_NUMBER: _ClassVar[int]
    list: _containers.RepeatedCompositeFieldContainer[EmitterEnvelopeState]
    def __init__(self, list: _Optional[_Iterable[_Union[EmitterEnvelopeState, _Mapping]]] = ...) -> None: ...

class Event(_message.Message):
    __slots__ = ("id", "type", "index", "itemCount", "checksum", "items")
    ID_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    INDEX_FIELD_NUMBER: _ClassVar[int]
    ITEMCOUNT_FIELD_NUMBER: _ClassVar[int]
    CHECKSUM_FIELD_NUMBER: _ClassVar[int]
    ITEMS_FIELD_NUMBER: _ClassVar[int]
    id: bytes
    type: str
    index: int
    itemCount: int
    checksum: int
    items: _containers.RepeatedScalarFieldContainer[bytes]
    def __init__(self, id: _Optional[bytes] = ..., type: _Optional[str] = ..., index: _Optional[int] = ..., itemCount: _Optional[int] = ..., checksum: _Optional[int] = ..., items: _Optional[_Iterable[bytes]] = ...) -> None: ...

class EventPosition(_message.Message):
    __slots__ = ("eventID", "index", "itemCount")
    EVENTID_FIELD_NUMBER: _ClassVar[int]
    INDEX_FIELD_NUMBER: _ClassVar[int]
    ITEMCOUNT_FIELD_NUMBER: _ClassVar[int]
    eventID: bytes
    index: int
    itemCount: int
    def __init__(self, eventID: _Optional[bytes] = ..., index: _Optional[int] = ..., itemCount: _Optional[int] = ...) -> None: ...

class AckResultRequest(_message.Message):
    __slots__ = ("processID",)
    PROCESSID_FIELD_NUMBER: _ClassVar[int]
    processID: bytes
    def __init__(self, processID: _Optional[bytes] = ...) -> None: ...

class GetEnvelopeStateRequest(_message.Message):
    __slots__ = ("id",)
    ID_FIELD_NUMBER: _ClassVar[int]
    id: bytes
    def __init__(self, id: _Optional[bytes] = ...) -> None: ...

class EnvelopePosition(_message.Message):
    __slots__ = ("envelopeID", "start", "complete", "eventPositions")
    ENVELOPEID_FIELD_NUMBER: _ClassVar[int]
    START_FIELD_NUMBER: _ClassVar[int]
    COMPLETE_FIELD_NUMBER: _ClassVar[int]
    EVENTPOSITIONS_FIELD_NUMBER: _ClassVar[int]
    envelopeID: bytes
    start: bool
    complete: bool
    eventPositions: _containers.RepeatedCompositeFieldContainer[EventPosition]
    def __init__(self, envelopeID: _Optional[bytes] = ..., start: bool = ..., complete: bool = ..., eventPositions: _Optional[_Iterable[_Union[EventPosition, _Mapping]]] = ...) -> None: ...

class ProcessingContext(_message.Message):
    __slots__ = ("processID", "nodeID")
    PROCESSID_FIELD_NUMBER: _ClassVar[int]
    NODEID_FIELD_NUMBER: _ClassVar[int]
    processID: bytes
    nodeID: str
    def __init__(self, processID: _Optional[bytes] = ..., nodeID: _Optional[str] = ...) -> None: ...

class Envelope(_message.Message):
    __slots__ = ("id", "eventIDs", "events", "last")
    ID_FIELD_NUMBER: _ClassVar[int]
    EVENTIDS_FIELD_NUMBER: _ClassVar[int]
    EVENTS_FIELD_NUMBER: _ClassVar[int]
    LAST_FIELD_NUMBER: _ClassVar[int]
    id: bytes
    eventIDs: _containers.RepeatedScalarFieldContainer[bytes]
    events: _containers.RepeatedCompositeFieldContainer[Event]
    last: bool
    def __init__(self, id: _Optional[bytes] = ..., eventIDs: _Optional[_Iterable[bytes]] = ..., events: _Optional[_Iterable[_Union[Event, _Mapping]]] = ..., last: bool = ...) -> None: ...

class EnvelopeFragmentAndPosition(_message.Message):
    __slots__ = ("fragment", "position")
    FRAGMENT_FIELD_NUMBER: _ClassVar[int]
    POSITION_FIELD_NUMBER: _ClassVar[int]
    fragment: Envelope
    position: EnvelopePosition
    def __init__(self, fragment: _Optional[_Union[Envelope, _Mapping]] = ..., position: _Optional[_Union[EnvelopePosition, _Mapping]] = ...) -> None: ...

class EnvelopeAck(_message.Message):
    __slots__ = ("id", "status", "reason")
    class ReceptionStatus(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        NOSTATUS: _ClassVar[EnvelopeAck.ReceptionStatus]
        RECEIVING: _ClassVar[EnvelopeAck.ReceptionStatus]
        ACCEPTED: _ClassVar[EnvelopeAck.ReceptionStatus]
        ERROR: _ClassVar[EnvelopeAck.ReceptionStatus]
    NOSTATUS: EnvelopeAck.ReceptionStatus
    RECEIVING: EnvelopeAck.ReceptionStatus
    ACCEPTED: EnvelopeAck.ReceptionStatus
    ERROR: EnvelopeAck.ReceptionStatus
    ID_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    REASON_FIELD_NUMBER: _ClassVar[int]
    id: bytes
    status: EnvelopeAck.ReceptionStatus
    reason: str
    def __init__(self, id: _Optional[bytes] = ..., status: _Optional[_Union[EnvelopeAck.ReceptionStatus, str]] = ..., reason: _Optional[str] = ...) -> None: ...

class EnvelopeTarget(_message.Message):
    __slots__ = ("actorID", "nodeID", "input")
    ACTORID_FIELD_NUMBER: _ClassVar[int]
    NODEID_FIELD_NUMBER: _ClassVar[int]
    INPUT_FIELD_NUMBER: _ClassVar[int]
    actorID: bytes
    nodeID: str
    input: str
    def __init__(self, actorID: _Optional[bytes] = ..., nodeID: _Optional[str] = ..., input: _Optional[str] = ...) -> None: ...

class OutputRequest(_message.Message):
    __slots__ = ("context", "output", "close", "envelope")
    CONTEXT_FIELD_NUMBER: _ClassVar[int]
    OUTPUT_FIELD_NUMBER: _ClassVar[int]
    CLOSE_FIELD_NUMBER: _ClassVar[int]
    ENVELOPE_FIELD_NUMBER: _ClassVar[int]
    context: ProcessingContext
    output: str
    close: bool
    envelope: Envelope
    def __init__(self, context: _Optional[_Union[ProcessingContext, _Mapping]] = ..., output: _Optional[str] = ..., close: bool = ..., envelope: _Optional[_Union[Envelope, _Mapping]] = ...) -> None: ...

class PipelineInfo(_message.Message):
    __slots__ = ("id", "name", "description", "version", "status")
    class Status(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        DRAFT: _ClassVar[PipelineInfo.Status]
        ACTIVE: _ClassVar[PipelineInfo.Status]
        INACTIVE: _ClassVar[PipelineInfo.Status]
    DRAFT: PipelineInfo.Status
    ACTIVE: PipelineInfo.Status
    INACTIVE: PipelineInfo.Status
    ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    VERSION_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    id: bytes
    name: str
    description: str
    version: str
    status: PipelineInfo.Status
    def __init__(self, id: _Optional[bytes] = ..., name: _Optional[str] = ..., description: _Optional[str] = ..., version: _Optional[str] = ..., status: _Optional[_Union[PipelineInfo.Status, str]] = ...) -> None: ...

class LogEntry(_message.Message):
    __slots__ = ("envelopeID", "actorID", "processID", "nodeID", "message")
    ENVELOPEID_FIELD_NUMBER: _ClassVar[int]
    ACTORID_FIELD_NUMBER: _ClassVar[int]
    PROCESSID_FIELD_NUMBER: _ClassVar[int]
    NODEID_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    envelopeID: bytes
    actorID: bytes
    processID: bytes
    nodeID: str
    message: LogMessage
    def __init__(self, envelopeID: _Optional[bytes] = ..., actorID: _Optional[bytes] = ..., processID: _Optional[bytes] = ..., nodeID: _Optional[str] = ..., message: _Optional[_Union[LogMessage, _Mapping]] = ...) -> None: ...

class PMProcess(_message.Message):
    __slots__ = ("process", "level", "status", "comment", "logs")
    class Status(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        DEFAULT: _ClassVar[PMProcess.Status]
        NEW: _ClassVar[PMProcess.Status]
        OPENED: _ClassVar[PMProcess.Status]
        CLOSED: _ClassVar[PMProcess.Status]
    DEFAULT: PMProcess.Status
    NEW: PMProcess.Status
    OPENED: PMProcess.Status
    CLOSED: PMProcess.Status
    PROCESS_FIELD_NUMBER: _ClassVar[int]
    LEVEL_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    COMMENT_FIELD_NUMBER: _ClassVar[int]
    LOGS_FIELD_NUMBER: _ClassVar[int]
    process: Process
    level: LogLevel
    status: PMProcess.Status
    comment: str
    logs: _containers.RepeatedCompositeFieldContainer[LogEntry]
    def __init__(self, process: _Optional[_Union[Process, _Mapping]] = ..., level: _Optional[_Union[LogLevel, str]] = ..., status: _Optional[_Union[PMProcess.Status, str]] = ..., comment: _Optional[str] = ..., logs: _Optional[_Iterable[_Union[LogEntry, _Mapping]]] = ...) -> None: ...

class Process(_message.Message):
    __slots__ = ("id", "groupID", "replayOf", "triggerEmitterID", "triggerEnvelopeID", "pipelineID", "status", "state", "createdAt")
    class Status(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        NOSTATUS: _ClassVar[Process.Status]
        INITIAL: _ClassVar[Process.Status]
        RUNNING: _ClassVar[Process.Status]
        PAUSED: _ClassVar[Process.Status]
        DONE: _ClassVar[Process.Status]
        ERROR: _ClassVar[Process.Status]
    NOSTATUS: Process.Status
    INITIAL: Process.Status
    RUNNING: Process.Status
    PAUSED: Process.Status
    DONE: Process.Status
    ERROR: Process.Status
    ID_FIELD_NUMBER: _ClassVar[int]
    GROUPID_FIELD_NUMBER: _ClassVar[int]
    REPLAYOF_FIELD_NUMBER: _ClassVar[int]
    TRIGGEREMITTERID_FIELD_NUMBER: _ClassVar[int]
    TRIGGERENVELOPEID_FIELD_NUMBER: _ClassVar[int]
    PIPELINEID_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    STATE_FIELD_NUMBER: _ClassVar[int]
    CREATEDAT_FIELD_NUMBER: _ClassVar[int]
    id: bytes
    groupID: bytes
    replayOf: bytes
    triggerEmitterID: bytes
    triggerEnvelopeID: bytes
    pipelineID: bytes
    status: Process.Status
    state: str
    createdAt: _timestamp_pb2.Timestamp
    def __init__(self, id: _Optional[bytes] = ..., groupID: _Optional[bytes] = ..., replayOf: _Optional[bytes] = ..., triggerEmitterID: _Optional[bytes] = ..., triggerEnvelopeID: _Optional[bytes] = ..., pipelineID: _Optional[bytes] = ..., status: _Optional[_Union[Process.Status, str]] = ..., state: _Optional[str] = ..., createdAt: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...

class TimeRange(_message.Message):
    __slots__ = ("to",)
    FROM_FIELD_NUMBER: _ClassVar[int]
    TO_FIELD_NUMBER: _ClassVar[int]
    to: _timestamp_pb2.Timestamp
    def __init__(self, to: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., **kwargs) -> None: ...

class ProcessFilter(_message.Message):
    __slots__ = ("id", "groupID", "replayOf", "triggerEmitterID", "triggerEnvelopeID", "createdAt", "pipelineID", "envelopeID", "status", "statusChangedFrom", "statusChangedTo", "statusChanged", "resultAcked")
    ID_FIELD_NUMBER: _ClassVar[int]
    GROUPID_FIELD_NUMBER: _ClassVar[int]
    REPLAYOF_FIELD_NUMBER: _ClassVar[int]
    TRIGGEREMITTERID_FIELD_NUMBER: _ClassVar[int]
    TRIGGERENVELOPEID_FIELD_NUMBER: _ClassVar[int]
    CREATEDAT_FIELD_NUMBER: _ClassVar[int]
    PIPELINEID_FIELD_NUMBER: _ClassVar[int]
    ENVELOPEID_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    STATUSCHANGEDFROM_FIELD_NUMBER: _ClassVar[int]
    STATUSCHANGEDTO_FIELD_NUMBER: _ClassVar[int]
    STATUSCHANGED_FIELD_NUMBER: _ClassVar[int]
    RESULTACKED_FIELD_NUMBER: _ClassVar[int]
    id: _containers.RepeatedScalarFieldContainer[bytes]
    groupID: _containers.RepeatedScalarFieldContainer[bytes]
    replayOf: _containers.RepeatedScalarFieldContainer[bytes]
    triggerEmitterID: _containers.RepeatedScalarFieldContainer[bytes]
    triggerEnvelopeID: _containers.RepeatedScalarFieldContainer[bytes]
    createdAt: TimeRange
    pipelineID: _containers.RepeatedScalarFieldContainer[bytes]
    envelopeID: _containers.RepeatedScalarFieldContainer[bytes]
    status: _containers.RepeatedScalarFieldContainer[Process.Status]
    statusChangedFrom: _timestamp_pb2.Timestamp
    statusChangedTo: _timestamp_pb2.Timestamp
    statusChanged: TimeRange
    resultAcked: _containers.RepeatedScalarFieldContainer[bool]
    def __init__(self, id: _Optional[_Iterable[bytes]] = ..., groupID: _Optional[_Iterable[bytes]] = ..., replayOf: _Optional[_Iterable[bytes]] = ..., triggerEmitterID: _Optional[_Iterable[bytes]] = ..., triggerEnvelopeID: _Optional[_Iterable[bytes]] = ..., createdAt: _Optional[_Union[TimeRange, _Mapping]] = ..., pipelineID: _Optional[_Iterable[bytes]] = ..., envelopeID: _Optional[_Iterable[bytes]] = ..., status: _Optional[_Iterable[_Union[Process.Status, str]]] = ..., statusChangedFrom: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., statusChangedTo: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., statusChanged: _Optional[_Union[TimeRange, _Mapping]] = ..., resultAcked: _Optional[_Iterable[bool]] = ...) -> None: ...

class Registration(_message.Message):
    __slots__ = ("id", "registrationStatus", "signedCertificate", "serverCA", "actorList")
    class Status(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        PENDING: _ClassVar[Registration.Status]
        ACCEPTED: _ClassVar[Registration.Status]
        REJECTED: _ClassVar[Registration.Status]
    PENDING: Registration.Status
    ACCEPTED: Registration.Status
    REJECTED: Registration.Status
    ID_FIELD_NUMBER: _ClassVar[int]
    REGISTRATIONSTATUS_FIELD_NUMBER: _ClassVar[int]
    SIGNEDCERTIFICATE_FIELD_NUMBER: _ClassVar[int]
    SERVERCA_FIELD_NUMBER: _ClassVar[int]
    ACTORLIST_FIELD_NUMBER: _ClassVar[int]
    id: bytes
    registrationStatus: Registration.Status
    signedCertificate: str
    serverCA: str
    actorList: _containers.RepeatedCompositeFieldContainer[Actor]
    def __init__(self, id: _Optional[bytes] = ..., registrationStatus: _Optional[_Union[Registration.Status, str]] = ..., signedCertificate: _Optional[str] = ..., serverCA: _Optional[str] = ..., actorList: _Optional[_Iterable[_Union[Actor, _Mapping]]] = ...) -> None: ...

class StringReply(_message.Message):
    __slots__ = ("value",)
    VALUE_FIELD_NUMBER: _ClassVar[int]
    value: str
    def __init__(self, value: _Optional[str] = ...) -> None: ...

class ActorLogRequest(_message.Message):
    __slots__ = ("envelopeID", "Context", "messages")
    ENVELOPEID_FIELD_NUMBER: _ClassVar[int]
    CONTEXT_FIELD_NUMBER: _ClassVar[int]
    MESSAGES_FIELD_NUMBER: _ClassVar[int]
    envelopeID: bytes
    Context: ProcessingContext
    messages: _containers.RepeatedCompositeFieldContainer[LogMessage]
    def __init__(self, envelopeID: _Optional[bytes] = ..., Context: _Optional[_Union[ProcessingContext, _Mapping]] = ..., messages: _Optional[_Iterable[_Union[LogMessage, _Mapping]]] = ...) -> None: ...

class ActorProcessRequest(_message.Message):
    __slots__ = ("context", "inputs")
    class Input(_message.Message):
        __slots__ = ("name", "close", "envelope", "position")
        NAME_FIELD_NUMBER: _ClassVar[int]
        CLOSE_FIELD_NUMBER: _ClassVar[int]
        ENVELOPE_FIELD_NUMBER: _ClassVar[int]
        POSITION_FIELD_NUMBER: _ClassVar[int]
        name: str
        close: bool
        envelope: Envelope
        position: EnvelopePosition
        def __init__(self, name: _Optional[str] = ..., close: bool = ..., envelope: _Optional[_Union[Envelope, _Mapping]] = ..., position: _Optional[_Union[EnvelopePosition, _Mapping]] = ...) -> None: ...
    CONTEXT_FIELD_NUMBER: _ClassVar[int]
    INPUTS_FIELD_NUMBER: _ClassVar[int]
    context: ProcessingContext
    inputs: _containers.RepeatedCompositeFieldContainer[ActorProcessRequest.Input]
    def __init__(self, context: _Optional[_Union[ProcessingContext, _Mapping]] = ..., inputs: _Optional[_Iterable[_Union[ActorProcessRequest.Input, _Mapping]]] = ...) -> None: ...

class ActorProcessingState(_message.Message):
    __slots__ = ("context", "status", "messages", "ActorLeaving")
    class Status(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        PENDING: _ClassVar[ActorProcessingState.Status]
        RUNNING: _ClassVar[ActorProcessingState.Status]
        SUCCESS: _ClassVar[ActorProcessingState.Status]
        ERROR: _ClassVar[ActorProcessingState.Status]
    PENDING: ActorProcessingState.Status
    RUNNING: ActorProcessingState.Status
    SUCCESS: ActorProcessingState.Status
    ERROR: ActorProcessingState.Status
    CONTEXT_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    MESSAGES_FIELD_NUMBER: _ClassVar[int]
    ACTORLEAVING_FIELD_NUMBER: _ClassVar[int]
    context: ProcessingContext
    status: ActorProcessingState.Status
    messages: _containers.RepeatedCompositeFieldContainer[LogMessage]
    ActorLeaving: bool
    def __init__(self, context: _Optional[_Union[ProcessingContext, _Mapping]] = ..., status: _Optional[_Union[ActorProcessingState.Status, str]] = ..., messages: _Optional[_Iterable[_Union[LogMessage, _Mapping]]] = ..., ActorLeaving: bool = ...) -> None: ...

class ActorReadyMsg(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class ClientGetActorsRequest(_message.Message):
    __slots__ = ("actorID",)
    ACTORID_FIELD_NUMBER: _ClassVar[int]
    actorID: bytes
    def __init__(self, actorID: _Optional[bytes] = ...) -> None: ...

class ClientGetActorsReply(_message.Message):
    __slots__ = ("actors",)
    ACTORS_FIELD_NUMBER: _ClassVar[int]
    actors: _containers.RepeatedCompositeFieldContainer[Actor]
    def __init__(self, actors: _Optional[_Iterable[_Union[Actor, _Mapping]]] = ...) -> None: ...

class RegistrationRequest(_message.Message):
    __slots__ = ("name", "type", "csr", "actorList")
    NAME_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    CSR_FIELD_NUMBER: _ClassVar[int]
    ACTORLIST_FIELD_NUMBER: _ClassVar[int]
    name: str
    type: Account.Type
    csr: str
    actorList: _containers.RepeatedCompositeFieldContainer[Actor]
    def __init__(self, name: _Optional[str] = ..., type: _Optional[_Union[Account.Type, str]] = ..., csr: _Optional[str] = ..., actorList: _Optional[_Iterable[_Union[Actor, _Mapping]]] = ...) -> None: ...

class SurveyRequest(_message.Message):
    __slots__ = ("onlineStatus",)
    ONLINESTATUS_FIELD_NUMBER: _ClassVar[int]
    onlineStatus: bool
    def __init__(self, onlineStatus: bool = ...) -> None: ...

class GetSessionTokenRequest(_message.Message):
    __slots__ = ("expiresIn", "invalidateToken")
    EXPIRESIN_FIELD_NUMBER: _ClassVar[int]
    INVALIDATETOKEN_FIELD_NUMBER: _ClassVar[int]
    expiresIn: int
    invalidateToken: str
    def __init__(self, expiresIn: _Optional[int] = ..., invalidateToken: _Optional[str] = ...) -> None: ...

class SessionToken(_message.Message):
    __slots__ = ("token", "validUntil")
    TOKEN_FIELD_NUMBER: _ClassVar[int]
    VALIDUNTIL_FIELD_NUMBER: _ClassVar[int]
    token: str
    validUntil: _timestamp_pb2.Timestamp
    def __init__(self, token: _Optional[str] = ..., validUntil: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...
