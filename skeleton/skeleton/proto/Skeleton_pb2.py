# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# NO CHECKED-IN PROTOBUF GENCODE
# source: skeleton/proto/Skeleton.proto
# Protobuf Python Version: 5.27.3
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import runtime_version as _runtime_version
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
_runtime_version.ValidateProtobufRuntimeVersion(
    _runtime_version.Domain.PUBLIC,
    5,
    27,
    3,
    '',
    'skeleton/proto/Skeleton.proto'
)
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


from _.records import Protobuf_pb2 as ___dot_records_dot_Protobuf__pb2


DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x1dskeleton/proto/Skeleton.proto\x12\x0eskeleton.proto\x1a\x18_/records/Protobuf.proto\"0\n\x08Skeleton\x12\x0e\n\x06\x66ield1\x18\x01 \x01(\t\x12\x0e\n\x06\x66ield2\x18\x02 \x01(\t:\x04\x98\xb5\x18\x01\"\xf6\x01\n\x07Reports\x12.\n\x06single\x18\x01 \x01(\x0b\x32\x1e.skeleton.proto.Reports.Report\x12\x30\n\x08multiple\x18\x02 \x03(\x0b\x32\x1e.skeleton.proto.Reports.Report\x12\x11\n\x03req\x18\x03 \x01(\tB\x04\x98\xb5\x18\x01\x1ap\n\x06Report\x12\x0e\n\x06source\x18\x01 \x01(\t\x12\r\n\x05\x63ount\x18\x02 \x01(\x05\x12\x31\n\x04\x64\x65\x65p\x18\x03 \x01(\x0b\x32#.skeleton.proto.Reports.Report.Deep\x1a\x14\n\x04\x44\x65\x65p\x12\x0c\n\x04\x64\x65\x65p\x18\x01 \x01(\t:\x04\x98\xb5\x18\x01\" \n\x07Numbers\x12\x0f\n\x07reports\x18\x01 \x03(\x05:\x04\x90\xb5\x18\x01\"9\n\x07Message\x12\x0e\n\x06\x66ield1\x18\x01 \x01(\t\x12\x0e\n\x06\x66ield2\x18\x02 \x01(\t:\x0e\x8a\xb5\x18\nmessage_id\"/\n\x07NoTable\x12\x0e\n\x06\x66ield1\x18\x01 \x01(\t\x12\x0e\n\x06\x66ield2\x18\x02 \x01(\t:\x04\x98\xb5\x18\x01\"-\n\x05NoWeb\x12\x14\n\x06\x66ield1\x18\x01 \x01(\tB\x04\x88\xb5\x18\x01\x12\x0e\n\x06\x66ield2\x18\x02 \x01(\tb\x06proto3')

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'skeleton.proto.Skeleton_pb2', _globals)
if not _descriptor._USE_C_DESCRIPTORS:
  DESCRIPTOR._loaded_options = None
  _globals['_SKELETON']._loaded_options = None
  _globals['_SKELETON']._serialized_options = b'\230\265\030\001'
  _globals['_REPORTS'].fields_by_name['req']._loaded_options = None
  _globals['_REPORTS'].fields_by_name['req']._serialized_options = b'\230\265\030\001'
  _globals['_REPORTS']._loaded_options = None
  _globals['_REPORTS']._serialized_options = b'\230\265\030\001'
  _globals['_NUMBERS']._loaded_options = None
  _globals['_NUMBERS']._serialized_options = b'\220\265\030\001'
  _globals['_MESSAGE']._loaded_options = None
  _globals['_MESSAGE']._serialized_options = b'\212\265\030\nmessage_id'
  _globals['_NOTABLE']._loaded_options = None
  _globals['_NOTABLE']._serialized_options = b'\230\265\030\001'
  _globals['_NOWEB'].fields_by_name['field1']._loaded_options = None
  _globals['_NOWEB'].fields_by_name['field1']._serialized_options = b'\210\265\030\001'
  _globals['_SKELETON']._serialized_start=75
  _globals['_SKELETON']._serialized_end=123
  _globals['_REPORTS']._serialized_start=126
  _globals['_REPORTS']._serialized_end=372
  _globals['_REPORTS_REPORT']._serialized_start=254
  _globals['_REPORTS_REPORT']._serialized_end=366
  _globals['_REPORTS_REPORT_DEEP']._serialized_start=346
  _globals['_REPORTS_REPORT_DEEP']._serialized_end=366
  _globals['_NUMBERS']._serialized_start=374
  _globals['_NUMBERS']._serialized_end=406
  _globals['_MESSAGE']._serialized_start=408
  _globals['_MESSAGE']._serialized_end=465
  _globals['_NOTABLE']._serialized_start=467
  _globals['_NOTABLE']._serialized_end=514
  _globals['_NOWEB']._serialized_start=516
  _globals['_NOWEB']._serialized_end=561
# @@protoc_insertion_point(module_scope)
