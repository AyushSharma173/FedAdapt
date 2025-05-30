# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# NO CHECKED-IN PROTOBUF GENCODE
# source: fedscale/cloud/channels/job_api.proto
# Protobuf Python Version: 5.29.0
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import runtime_version as _runtime_version
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
_runtime_version.ValidateProtobufRuntimeVersion(
    _runtime_version.Domain.PUBLIC,
    5,
    29,
    0,
    '',
    'fedscale/cloud/channels/job_api.proto'
)
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n%fedscale/cloud/channels/job_api.proto\x12\x08\x66\x65\x64scale\";\n\x0eServerResponse\x12\r\n\x05\x65vent\x18\x01 \x01(\t\x12\x0c\n\x04meta\x18\x02 \x01(\x0c\x12\x0c\n\x04\x64\x61ta\x18\x03 \x01(\x0c\"P\n\x0fRegisterRequest\x12\x11\n\tclient_id\x18\x01 \x01(\t\x12\x13\n\x0b\x65xecutor_id\x18\x02 \x01(\t\x12\x15\n\rexecutor_info\x18\x03 \x01(\x0c\"5\n\x0bPingRequest\x12\x11\n\tclient_id\x18\x01 \x01(\t\x12\x13\n\x0b\x65xecutor_id\x18\x02 \x01(\t\"\x8f\x01\n\x0f\x43ompleteRequest\x12\x11\n\tclient_id\x18\x01 \x01(\t\x12\x13\n\x0b\x65xecutor_id\x18\x02 \x01(\t\x12\r\n\x05\x65vent\x18\x03 \x01(\t\x12\x0e\n\x06status\x18\x04 \x01(\x08\x12\x0b\n\x03msg\x18\x05 \x01(\t\x12\x13\n\x0bmeta_result\x18\x06 \x01(\t\x12\x13\n\x0b\x64\x61ta_result\x18\x07 \x01(\x0c\"&\n\rStatusRequest\x12\x15\n\rexperiment_id\x18\x01 \x01(\t\"o\n\x0bStatusReply\x12\x15\n\rcurrent_round\x18\x01 \x01(\x05\x12\x12\n\nis_running\x18\x02 \x01(\x08\x12\x1c\n\x14global_virtual_clock\x18\x03 \x01(\x01\x12\x17\n\x0fsampled_clients\x18\x04 \x03(\t\"\x1f\n\x0eMetricsRequest\x12\r\n\x05round\x18\x01 \x01(\x05\"S\n\rClientMetrics\x12\x11\n\tclient_id\x18\x01 \x01(\x05\x12\x0c\n\x04loss\x18\x02 \x01(\x01\x12\x0f\n\x07utility\x18\x03 \x01(\x01\x12\x10\n\x08\x64uration\x18\x04 \x01(\x01\"\x8a\x01\n\x0cMetricsReply\x12\r\n\x05round\x18\x01 \x01(\x05\x12\x11\n\ttest_loss\x18\x02 \x01(\x01\x12\x16\n\x0etest_accuracy1\x18\x03 \x01(\x01\x12\x16\n\x0etest_accuracy5\x18\x04 \x01(\x01\x12(\n\x07\x63lients\x18\x05 \x03(\x0b\x32\x17.fedscale.ClientMetrics2\xfc\x02\n\nJobService\x12H\n\x0f\x43LIENT_REGISTER\x12\x19.fedscale.RegisterRequest\x1a\x18.fedscale.ServerResponse\"\x00\x12@\n\x0b\x43LIENT_PING\x12\x15.fedscale.PingRequest\x1a\x18.fedscale.ServerResponse\"\x00\x12R\n\x19\x43LIENT_EXECUTE_COMPLETION\x12\x19.fedscale.CompleteRequest\x1a\x18.fedscale.ServerResponse\"\x00\x12G\n\x13GetAggregatorStatus\x12\x17.fedscale.StatusRequest\x1a\x15.fedscale.StatusReply\"\x00\x12\x45\n\x0fGetRoundMetrics\x12\x18.fedscale.MetricsRequest\x1a\x16.fedscale.MetricsReply\"\x00\x62\x06proto3')

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'fedscale.cloud.channels.job_api_pb2', _globals)
if not _descriptor._USE_C_DESCRIPTORS:
  DESCRIPTOR._loaded_options = None
  _globals['_SERVERRESPONSE']._serialized_start=51
  _globals['_SERVERRESPONSE']._serialized_end=110
  _globals['_REGISTERREQUEST']._serialized_start=112
  _globals['_REGISTERREQUEST']._serialized_end=192
  _globals['_PINGREQUEST']._serialized_start=194
  _globals['_PINGREQUEST']._serialized_end=247
  _globals['_COMPLETEREQUEST']._serialized_start=250
  _globals['_COMPLETEREQUEST']._serialized_end=393
  _globals['_STATUSREQUEST']._serialized_start=395
  _globals['_STATUSREQUEST']._serialized_end=433
  _globals['_STATUSREPLY']._serialized_start=435
  _globals['_STATUSREPLY']._serialized_end=546
  _globals['_METRICSREQUEST']._serialized_start=548
  _globals['_METRICSREQUEST']._serialized_end=579
  _globals['_CLIENTMETRICS']._serialized_start=581
  _globals['_CLIENTMETRICS']._serialized_end=664
  _globals['_METRICSREPLY']._serialized_start=667
  _globals['_METRICSREPLY']._serialized_end=805
  _globals['_JOBSERVICE']._serialized_start=808
  _globals['_JOBSERVICE']._serialized_end=1188
# @@protoc_insertion_point(module_scope)
