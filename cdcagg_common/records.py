# Copyright CESSDA ERIC 2021-2025
#
# Licensed under the EUPL, Version 1.2 (the "License"); you may not
# use this file except in compliance with the License.
# You may obtain a copy of the License at
# https://joinup.ec.europa.eu/collection/eupl/eupl-text-eupl-12
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Define CDC Aggregator records.

These records define the internal data model for CDC Aggregator. They
are reflected to the MongoDB database and DocStore record validation
is dynamically constructed by consulting the record properties.
"""
from itertools import chain
from kuha_common.document_store.field_types import FieldTypeFactory
from kuha_common.document_store import records


class RecordBase(records.RecordBase):
    """Base class for all CDC Aggregator records.

    Subclass of :class:`kuha_common.document_store.records`, which
    defines additional :attr:`_provenance`, :attr:`_direct_base_url`
    and :attr:`_aggregator_identifier` attributes.
    """

    _provenance = FieldTypeFactory('_provenance', 'harvest_date',
                                   attrs=['altered', 'base_url',
                                          'identifier', 'datestamp',
                                          'direct',
                                          'metadata_namespace'],
                                   localizable=False)
    _direct_base_url = FieldTypeFactory('_direct_base_url',
                                        localizable=False, single_value=True)
    _aggregator_identifier = FieldTypeFactory('_aggregator_identifier',
                                              localizable=False, single_value=True)

    def __init__(self, document_store_dictionary=None):
        """Instantiate a record instance.

        If document_store_dictionary is given on init, the object is
        assumed an existing record and no attributes for new record are
        created.

        :note: Do not instantiate directly but use from a subclass.

        :param dict or None document_store_dictionary: Record response from DocStore converted from JSON by Python dict.
        :returns: Instance of a record subclass.
        """
        self._provenance = self._provenance.fabricate()
        self._direct_base_url = self._direct_base_url.fabricate()
        self._aggregator_identifier = self._aggregator_identifier.fabricate()
        if document_store_dictionary is not None:
            self._import_provenance(document_store_dictionary)
        super().__init__(document_store_dictionary)

    def set_aggregator_identifier(self, value):
        """Set aggregator identifier.

        Silently overwrites previous value, if any.

        :param str value: Aggregator identifier
        """
        self._aggregator_identifier.set_value(value)

    def set_direct_base_url(self, value):
        """Set direct base url

        :param str value: direct base url
        :raises: :exc:`ValueError` if direct base url is already set
        """
        if self._direct_base_url.get_value() is not None:
            raise ValueError("Direct base url is already set")
        self._direct_base_url.set_value(value)

    def _import_provenance(self, dct):
        if self._provenance.name in dct:
            self._provenance.import_records(dct[self._provenance.name])
        if self._aggregator_identifier.name in dct:
            self._aggregator_identifier.import_records(dct[self._aggregator_identifier.name])
        if self._direct_base_url.name in dct:
            self._direct_base_url.import_records(dct[self._direct_base_url.name])

    def export_provenance_dict(self):
        """Export provenance info as a dictionary.

        :returns: Record's provenance info.
        :rtype: dict
        """
        dct = self._provenance.export_dict()
        dct.update(self._aggregator_identifier.export_dict())
        dct.update(self._direct_base_url.export_dict())
        return dct

    def export_dict(self, include_provenance=True, **kwargs):
        """Export record as a dict.

        Additional keyword arguments are passed to parent method
        :meth:`kuha_common.document_store.records.RecordBase.export_dict`

        :param bool include_provenance: Include provenance in export.
        :returns: Record as dictionary.
        :rtype: dict
        """
        dct = super().export_dict(**kwargs)
        if include_provenance:
            dct.update(self.export_provenance_dict())
        return dct


class Study(RecordBase, records.Study):
    """CDC Aggregator Study record.

    Subclass that multi-inherits :class:`RecordBase` and
    :class:`kuha_common.document_store.records.Study`
    """
    @classmethod
    def iterate_record_fields(cls):
        """Override iterate_record_fields to include fields from both
        inherited classes.

        :returns: iterator yielding record fields.
        :rtype: iterator
        """
        return chain(super().iterate_record_fields(), records.Study.iterate_record_fields())
