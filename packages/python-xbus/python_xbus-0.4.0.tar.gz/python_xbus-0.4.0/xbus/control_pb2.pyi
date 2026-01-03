from google.protobuf import timestamp_pb2 as _timestamp_pb2
from nrpc import nrpc_pb2 as _nrpc_pb2
from xbus import xbus_pb2 as _xbus_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class StorageType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    UNDEFINED: _ClassVar[StorageType]
    ACCOUNT: _ClassVar[StorageType]
    ACTOR: _ClassVar[StorageType]
    ENVELOPE: _ClassVar[StorageType]
    JOB: _ClassVar[StorageType]
    LOG: _ClassVar[StorageType]
    PASSWORD: _ClassVar[StorageType]
    PIPELINE: _ClassVar[StorageType]
    PROCESS: _ClassVar[StorageType]
    SESSION: _ClassVar[StorageType]
UNDEFINED: StorageType
ACCOUNT: StorageType
ACTOR: StorageType
ENVELOPE: StorageType
JOB: StorageType
LOG: StorageType
PASSWORD: StorageType
PIPELINE: StorageType
PROCESS: StorageType
SESSION: StorageType

class DebugInfoRequest(_message.Message):
    __slots__ = ("entry", "args", "format")
    ENTRY_FIELD_NUMBER: _ClassVar[int]
    ARGS_FIELD_NUMBER: _ClassVar[int]
    FORMAT_FIELD_NUMBER: _ClassVar[int]
    entry: str
    args: _containers.RepeatedScalarFieldContainer[str]
    format: str
    def __init__(self, entry: _Optional[str] = ..., args: _Optional[_Iterable[str]] = ..., format: _Optional[str] = ...) -> None: ...

class OctetStreamList(_message.Message):
    __slots__ = ("chunks", "progression", "maxProgression")
    class Chunk(_message.Message):
        __slots__ = ("data", "index")
        DATA_FIELD_NUMBER: _ClassVar[int]
        INDEX_FIELD_NUMBER: _ClassVar[int]
        data: bytes
        index: int
        def __init__(self, data: _Optional[bytes] = ..., index: _Optional[int] = ...) -> None: ...
    CHUNKS_FIELD_NUMBER: _ClassVar[int]
    PROGRESSION_FIELD_NUMBER: _ClassVar[int]
    MAXPROGRESSION_FIELD_NUMBER: _ClassVar[int]
    chunks: _containers.RepeatedCompositeFieldContainer[OctetStreamList.Chunk]
    progression: int
    maxProgression: int
    def __init__(self, chunks: _Optional[_Iterable[_Union[OctetStreamList.Chunk, _Mapping]]] = ..., progression: _Optional[int] = ..., maxProgression: _Optional[int] = ...) -> None: ...

class AccountListRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class AccountListReply(_message.Message):
    __slots__ = ("accountList",)
    ACCOUNTLIST_FIELD_NUMBER: _ClassVar[int]
    accountList: _containers.RepeatedCompositeFieldContainer[_xbus_pb2.Account]
    def __init__(self, accountList: _Optional[_Iterable[_Union[_xbus_pb2.Account, _Mapping]]] = ...) -> None: ...

class AccountUpdateRequest(_message.Message):
    __slots__ = ("account", "expire")
    ACCOUNT_FIELD_NUMBER: _ClassVar[int]
    EXPIRE_FIELD_NUMBER: _ClassVar[int]
    account: _xbus_pb2.Account
    expire: _timestamp_pb2.Timestamp
    def __init__(self, account: _Optional[_Union[_xbus_pb2.Account, _Mapping]] = ..., expire: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...

class AccountIDRequest(_message.Message):
    __slots__ = ("accountID",)
    ACCOUNTID_FIELD_NUMBER: _ClassVar[int]
    accountID: bytes
    def __init__(self, accountID: _Optional[bytes] = ...) -> None: ...

class AccountPasswordSetRequest(_message.Message):
    __slots__ = ("accountID", "password")
    ACCOUNTID_FIELD_NUMBER: _ClassVar[int]
    PASSWORD_FIELD_NUMBER: _ClassVar[int]
    accountID: bytes
    password: str
    def __init__(self, accountID: _Optional[bytes] = ..., password: _Optional[str] = ...) -> None: ...

class ActorRequest(_message.Message):
    __slots__ = ("actorList",)
    ACTORLIST_FIELD_NUMBER: _ClassVar[int]
    actorList: _containers.RepeatedCompositeFieldContainer[_xbus_pb2.Actor]
    def __init__(self, actorList: _Optional[_Iterable[_Union[_xbus_pb2.Actor, _Mapping]]] = ...) -> None: ...

class ActorReply(_message.Message):
    __slots__ = ("actorList",)
    ACTORLIST_FIELD_NUMBER: _ClassVar[int]
    actorList: _containers.RepeatedCompositeFieldContainer[_xbus_pb2.Actor]
    def __init__(self, actorList: _Optional[_Iterable[_Union[_xbus_pb2.Actor, _Mapping]]] = ...) -> None: ...

class StorageStat(_message.Message):
    __slots__ = ("entries",)
    class Entry(_message.Message):
        __slots__ = ("name", "type", "implementation", "count", "estimatedSize")
        NAME_FIELD_NUMBER: _ClassVar[int]
        TYPE_FIELD_NUMBER: _ClassVar[int]
        IMPLEMENTATION_FIELD_NUMBER: _ClassVar[int]
        COUNT_FIELD_NUMBER: _ClassVar[int]
        ESTIMATEDSIZE_FIELD_NUMBER: _ClassVar[int]
        name: str
        type: StorageType
        implementation: str
        count: int
        estimatedSize: int
        def __init__(self, name: _Optional[str] = ..., type: _Optional[_Union[StorageType, str]] = ..., implementation: _Optional[str] = ..., count: _Optional[int] = ..., estimatedSize: _Optional[int] = ...) -> None: ...
    ENTRIES_FIELD_NUMBER: _ClassVar[int]
    entries: _containers.RepeatedCompositeFieldContainer[StorageStat.Entry]
    def __init__(self, entries: _Optional[_Iterable[_Union[StorageStat.Entry, _Mapping]]] = ...) -> None: ...

class PipelineQueryRequest(_message.Message):
    __slots__ = ("name",)
    NAME_FIELD_NUMBER: _ClassVar[int]
    name: str
    def __init__(self, name: _Optional[str] = ...) -> None: ...

class PipelineQueryReply(_message.Message):
    __slots__ = ("pipelineList",)
    PIPELINELIST_FIELD_NUMBER: _ClassVar[int]
    pipelineList: _containers.RepeatedCompositeFieldContainer[_xbus_pb2.PipelineInfo]
    def __init__(self, pipelineList: _Optional[_Iterable[_Union[_xbus_pb2.PipelineInfo, _Mapping]]] = ...) -> None: ...

class PipelineSaveRequest(_message.Message):
    __slots__ = ("info", "graph")
    INFO_FIELD_NUMBER: _ClassVar[int]
    GRAPH_FIELD_NUMBER: _ClassVar[int]
    info: _xbus_pb2.PipelineInfo
    graph: str
    def __init__(self, info: _Optional[_Union[_xbus_pb2.PipelineInfo, _Mapping]] = ..., graph: _Optional[str] = ...) -> None: ...

class PipelineSaveReply(_message.Message):
    __slots__ = ("info", "graph", "isValid", "validationMessages")
    INFO_FIELD_NUMBER: _ClassVar[int]
    GRAPH_FIELD_NUMBER: _ClassVar[int]
    ISVALID_FIELD_NUMBER: _ClassVar[int]
    VALIDATIONMESSAGES_FIELD_NUMBER: _ClassVar[int]
    info: _xbus_pb2.PipelineInfo
    graph: str
    isValid: bool
    validationMessages: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, info: _Optional[_Union[_xbus_pb2.PipelineInfo, _Mapping]] = ..., graph: _Optional[str] = ..., isValid: bool = ..., validationMessages: _Optional[_Iterable[str]] = ...) -> None: ...

class PipelineSetStatusReply(_message.Message):
    __slots__ = ("info", "isValid", "validationMessages")
    INFO_FIELD_NUMBER: _ClassVar[int]
    ISVALID_FIELD_NUMBER: _ClassVar[int]
    VALIDATIONMESSAGES_FIELD_NUMBER: _ClassVar[int]
    info: _xbus_pb2.PipelineInfo
    isValid: bool
    validationMessages: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, info: _Optional[_Union[_xbus_pb2.PipelineInfo, _Mapping]] = ..., isValid: bool = ..., validationMessages: _Optional[_Iterable[str]] = ...) -> None: ...

class LogsPurgeRequest(_message.Message):
    __slots__ = ("before",)
    BEFORE_FIELD_NUMBER: _ClassVar[int]
    before: _timestamp_pb2.Timestamp
    def __init__(self, before: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...

class LogsPurgeReply(_message.Message):
    __slots__ = ("count",)
    COUNT_FIELD_NUMBER: _ClassVar[int]
    count: int
    def __init__(self, count: _Optional[int] = ...) -> None: ...

class PMProcessQueryRequest(_message.Message):
    __slots__ = ("level", "includeClosed", "processIDs", "returnLogs")
    LEVEL_FIELD_NUMBER: _ClassVar[int]
    INCLUDECLOSED_FIELD_NUMBER: _ClassVar[int]
    PROCESSIDS_FIELD_NUMBER: _ClassVar[int]
    RETURNLOGS_FIELD_NUMBER: _ClassVar[int]
    level: _xbus_pb2.LogLevel
    includeClosed: bool
    processIDs: _containers.RepeatedScalarFieldContainer[bytes]
    returnLogs: bool
    def __init__(self, level: _Optional[_Union[_xbus_pb2.LogLevel, str]] = ..., includeClosed: bool = ..., processIDs: _Optional[_Iterable[bytes]] = ..., returnLogs: bool = ...) -> None: ...

class PMProcessQueryReply(_message.Message):
    __slots__ = ("pMProcessList",)
    PMPROCESSLIST_FIELD_NUMBER: _ClassVar[int]
    pMProcessList: _containers.RepeatedCompositeFieldContainer[_xbus_pb2.PMProcess]
    def __init__(self, pMProcessList: _Optional[_Iterable[_Union[_xbus_pb2.PMProcess, _Mapping]]] = ...) -> None: ...

class PMProcessSetStatusRequest(_message.Message):
    __slots__ = ("processID", "status", "comment")
    PROCESSID_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    COMMENT_FIELD_NUMBER: _ClassVar[int]
    processID: bytes
    status: _xbus_pb2.PMProcess.Status
    comment: str
    def __init__(self, processID: _Optional[bytes] = ..., status: _Optional[_Union[_xbus_pb2.PMProcess.Status, str]] = ..., comment: _Optional[str] = ...) -> None: ...

class ProcessQueryRequest(_message.Message):
    __slots__ = ("filter",)
    FILTER_FIELD_NUMBER: _ClassVar[int]
    filter: _xbus_pb2.ProcessFilter
    def __init__(self, filter: _Optional[_Union[_xbus_pb2.ProcessFilter, _Mapping]] = ...) -> None: ...

class ProcessQueryReply(_message.Message):
    __slots__ = ("processList",)
    PROCESSLIST_FIELD_NUMBER: _ClassVar[int]
    processList: _containers.RepeatedCompositeFieldContainer[_xbus_pb2.Process]
    def __init__(self, processList: _Optional[_Iterable[_Union[_xbus_pb2.Process, _Mapping]]] = ...) -> None: ...

class ProcessSummary(_message.Message):
    __slots__ = ("entries",)
    class Entry(_message.Message):
        __slots__ = ("pipelineID", "emitterID", "status", "resultAcked", "count")
        PIPELINEID_FIELD_NUMBER: _ClassVar[int]
        EMITTERID_FIELD_NUMBER: _ClassVar[int]
        STATUS_FIELD_NUMBER: _ClassVar[int]
        RESULTACKED_FIELD_NUMBER: _ClassVar[int]
        COUNT_FIELD_NUMBER: _ClassVar[int]
        pipelineID: bytes
        emitterID: bytes
        status: _xbus_pb2.Process.Status
        resultAcked: bool
        count: int
        def __init__(self, pipelineID: _Optional[bytes] = ..., emitterID: _Optional[bytes] = ..., status: _Optional[_Union[_xbus_pb2.Process.Status, str]] = ..., resultAcked: bool = ..., count: _Optional[int] = ...) -> None: ...
    ENTRIES_FIELD_NUMBER: _ClassVar[int]
    entries: _containers.RepeatedCompositeFieldContainer[ProcessSummary.Entry]
    def __init__(self, entries: _Optional[_Iterable[_Union[ProcessSummary.Entry, _Mapping]]] = ...) -> None: ...

class ProcessControlRequest(_message.Message):
    __slots__ = ("processID", "command")
    class Command(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        NONE: _ClassVar[ProcessControlRequest.Command]
        PAUSE: _ClassVar[ProcessControlRequest.Command]
        RESUME: _ClassVar[ProcessControlRequest.Command]
        CANCEL: _ClassVar[ProcessControlRequest.Command]
        REPLAY: _ClassVar[ProcessControlRequest.Command]
    NONE: ProcessControlRequest.Command
    PAUSE: ProcessControlRequest.Command
    RESUME: ProcessControlRequest.Command
    CANCEL: ProcessControlRequest.Command
    REPLAY: ProcessControlRequest.Command
    PROCESSID_FIELD_NUMBER: _ClassVar[int]
    COMMAND_FIELD_NUMBER: _ClassVar[int]
    processID: bytes
    command: ProcessControlRequest.Command
    def __init__(self, processID: _Optional[bytes] = ..., command: _Optional[_Union[ProcessControlRequest.Command, str]] = ...) -> None: ...

class ProcessExportRequest(_message.Message):
    __slots__ = ("processIDs", "exportEnvelope", "exportJobs", "exportLogs", "exportProcessLogs", "envelopeSizeLimit", "logLevel", "exportFull")
    PROCESSIDS_FIELD_NUMBER: _ClassVar[int]
    EXPORTENVELOPE_FIELD_NUMBER: _ClassVar[int]
    EXPORTJOBS_FIELD_NUMBER: _ClassVar[int]
    EXPORTLOGS_FIELD_NUMBER: _ClassVar[int]
    EXPORTPROCESSLOGS_FIELD_NUMBER: _ClassVar[int]
    ENVELOPESIZELIMIT_FIELD_NUMBER: _ClassVar[int]
    LOGLEVEL_FIELD_NUMBER: _ClassVar[int]
    EXPORTFULL_FIELD_NUMBER: _ClassVar[int]
    processIDs: _containers.RepeatedScalarFieldContainer[bytes]
    exportEnvelope: bool
    exportJobs: bool
    exportLogs: bool
    exportProcessLogs: bool
    envelopeSizeLimit: int
    logLevel: _xbus_pb2.LogLevel
    exportFull: bool
    def __init__(self, processIDs: _Optional[_Iterable[bytes]] = ..., exportEnvelope: bool = ..., exportJobs: bool = ..., exportLogs: bool = ..., exportProcessLogs: bool = ..., envelopeSizeLimit: _Optional[int] = ..., logLevel: _Optional[_Union[_xbus_pb2.LogLevel, str]] = ..., exportFull: bool = ...) -> None: ...

class ProcessReplayRequest(_message.Message):
    __slots__ = ("process", "match")
    PROCESS_FIELD_NUMBER: _ClassVar[int]
    MATCH_FIELD_NUMBER: _ClassVar[int]
    process: _xbus_pb2.Process
    match: bool
    def __init__(self, process: _Optional[_Union[_xbus_pb2.Process, _Mapping]] = ..., match: bool = ...) -> None: ...

class ProcessExportReply(_message.Message):
    __slots__ = ("processList",)
    PROCESSLIST_FIELD_NUMBER: _ClassVar[int]
    processList: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, processList: _Optional[_Iterable[str]] = ...) -> None: ...

class ProcessPurgeRequest(_message.Message):
    __slots__ = ("processIDs",)
    PROCESSIDS_FIELD_NUMBER: _ClassVar[int]
    processIDs: _containers.RepeatedScalarFieldContainer[bytes]
    def __init__(self, processIDs: _Optional[_Iterable[bytes]] = ...) -> None: ...

class TaskProgress(_message.Message):
    __slots__ = ("message", "progression", "maxProgression")
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    PROGRESSION_FIELD_NUMBER: _ClassVar[int]
    MAXPROGRESSION_FIELD_NUMBER: _ClassVar[int]
    message: str
    progression: int
    maxProgression: int
    def __init__(self, message: _Optional[str] = ..., progression: _Optional[int] = ..., maxProgression: _Optional[int] = ...) -> None: ...
