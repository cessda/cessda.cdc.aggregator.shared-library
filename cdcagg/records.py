from itertools import chain
from kuha_common.document_store.field_types import FieldTypeFactory
from kuha_common.document_store import records


class RecordBase(records.RecordBase):

    _provenance = FieldTypeFactory('_provenance', 'harvest_date',
                                   attrs=['altered', 'base_url',
                                          'identifier', 'datestamp',
                                          'direct',
                                          'metadata_namespace'],
                                   localizable=False)
    # TODO __init__ & update & create

    def __init__(self, *args, **kwargs):
        self._provenance = self._provenance.fabricate()
        super().__init__(*args, **kwargs)

    def export_provenance_dict(self):
        dct = self._provenance.export_dict()
        records.dig_and_set(dct, records.path_join(self._provenance.get_name(),
                                                   self._provenance.sub_element.get_name()),
                            records.datetime_to_datestamp)
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
