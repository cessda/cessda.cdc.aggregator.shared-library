from itertools import chain
from kuha_common.document_store.field_types import FieldTypeFactory
from kuha_common.document_store import records


class RecordBase(records.RecordBase):

    _provenance = FieldTypeFactory('_provenance', 'harvest_date',
                                   attrs=['altered', 'base_url', 'identifier', 'datestamp',
                                          'metadata_namespace'],
                                   localizable=False)
    # TODO __init__ & update & create


class Study(RecordBase, records.Study):

    @classmethod
    def iterate_record_fields(cls):
        return chain(super().iterate_record_fields(), records.Study.iterate_record_fields())
