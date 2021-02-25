"""MongoDB properties"""
from collections import namedtuple
from motor.motor_tornado import MotorClient
from pymongo import (
    DESCENDING,
    ASCENDING
)
from . import (
    records,
    mdb_const
)


_COMMON_ISODATE_FIELDS = [
    records.RecordBase._metadata.attr_updated.path,
    records.RecordBase._metadata.attr_deleted.path,
    records.RecordBase._metadata.attr_created.path
]
_COMMON_INDEXES = [[(records.RecordBase._metadata.attr_updated.path, DESCENDING)]]
_COMMON_OBJECTID_FIELDS = [records.RecordBase._id.path]


def get_client(conn_uri):
    return MotorClient(conn_uri)


def _collection_validator(collection_name, record_class, required=None):
    # TODO how about record_status. Should it be required?
    required = required or []
    required.extend([attr.path for attr in [
        record_class._metadata.attr_created,
        record_class._metadata.attr_updated,
        record_class._metadata.attr_deleted,
        record_class._metadata.attr_cmm_type,
        record_class._metadata.attr_schema_version,
        record_class._metadata.attr_status
    ]])
    properties = {
        record_class._metadata.attr_created.path: {
            'bsonType': mdb_const.MDB_TYPE_DATE,
            'description': 'Must be date and is required'
        },
        record_class._metadata.attr_updated.path: {
            'bsonType': mdb_const.MDB_TYPE_DATE,
            'description': 'Must be date and is required'
        },
        record_class._metadata.attr_deleted.path: {
            'bsonType': [mdb_const.MDB_TYPE_DATE, mdb_const.MDB_TYPE_NULL],
            'description': 'Must be date or null and is required'
        },
        record_class._metadata.attr_schema_version.path: {
            'bsonType': mdb_const.MDB_TYPE_DOUBLE,
            'description': 'Must be double and is required'
        },
        record_class._metadata.attr_cmm_type.path: {
            'bsonType': mdb_const.MDB_TYPE_STRING,
            'pattern': "^{cmm_type}$".format(cmm_type=record_class.cmm_type),
            'description': 'Fixed string %s and is required' % (record_class.cmm_type,)
        }
    }
    return {
        '$jsonSchema': {
            'bsonType': 'object',
            'required': required,
            'properties': properties
        }
    }


Collection = namedtuple('Collection', ['name', 'validators', 'indexes_unique',
                                       'indexes', 'isodate_fields', 'object_id_fields'])


def _init_collection(name, validators, indexes_unique):
    return Collection(name=name, validators=validators, indexes_unique=indexes_unique,
                      indexes=list(_COMMON_INDEXES), isodate_fields=list(_COMMON_ISODATE_FIELDS),
                      object_id_fields=list(_COMMON_OBJECTID_FIELDS))


def studies_collection():
    validators = _collection_validator(records.Study.get_collection(),
                                       records.Study,
                                       required=[records.Study.study_number.path])
    indexes_unique = [[(records.Study.study_number.path, DESCENDING)]]
    return _init_collection(records.Study.get_collection(), validators, indexes_unique)
