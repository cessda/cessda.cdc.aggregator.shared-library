from itertools import chain
from uuid import uuid4
from kuha_common.document_store.field_types import FieldTypeFactory
from kuha_common.document_store import records


class RecordBase(records.RecordBase):

    _provenance = FieldTypeFactory('_provenance', 'harvest_date',
                                   attrs=['altered', 'base_url',
                                          'identifier', 'datestamp',
                                          'direct',
                                          'metadata_namespace'],
                                   localizable=False)
    _aggregator_identifier = FieldTypeFactory('_aggregator_identifier',
                                              localizable=False, single_value=True)

    def __init__(self, document_store_dictionary=None):
        self._provenance = self._provenance.fabricate()
        self._aggregator_identifier = self._aggregator_identifier.fabricate()
        if document_store_dictionary is not None:
            self._import_provenance(document_store_dictionary)
        super().__init__(document_store_dictionary)

    def _new_record(self):
        super()._new_record()
        self._aggregator_identifier.add_value(uuid4().hex)

    def _import_provenance(self, dct):
        if self._provenance.name in dct:
            self._provenance.import_records(dct[self._provenance.name])
        if self._aggregator_identifier.name in dct:
            self._aggregator_identifier.import_records(dct[self._aggregator_identifier.name])

    def export_provenance_dict(self):
        dct = self._provenance.export_dict()
        dct.update(self._aggregator_identifier.export_dict())
        return dct

    def export_dict(self, include_provenance=True, **kwargs):
        dct = super().export_dict(**kwargs)
        if include_provenance:
            dct.update(self.export_provenance_dict())
        return dct


class Study(RecordBase, records.Study):

    @classmethod
    def iterate_record_fields(cls):
        return chain(super().iterate_record_fields(), records.Study.iterate_record_fields())
