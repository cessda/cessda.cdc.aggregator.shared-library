from .records import Study


def list_records():
    return [Study]


def list_collection_names():
    return [Study.get_collection()]


def record_by_collection_name(collname):
    for rec in list_records():
        if rec.get_collection() == collname:
            return rec
    return None
