from .records import Study
from .mdb import studies_collection


_COLLECTIONS = {Study.get_collection(): studies_collection}


def list_records():
    return [records.Study]


def list_collection_names():
    return list(_COLLECTIONS)


def record_by_collection_name(collname):
    for rec in list_records():
        if rec.get_collection() == collname:
            return rec
    return None


def iter_collections():
    for coll in _COLLECTIONS.values():
        yield coll()
