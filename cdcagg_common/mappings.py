"""XML parsers that read XML and map the metadata to CDCAGG records.
"""
from urllib.parse import quote_plus
from kuha_common.document_store.mappings import ddi
from kuha_common.document_store.records import (
    datetime_now,
    datetime_to_datestamp
)
from cdcagg_common.records import Study


OAI_NS = {'oai': 'http://www.openarchives.org/OAI/2.0/',
          'oai_p': 'http://www.openarchives.org/OAI/2.0/provenance'}


def _indirect_provenances_from_oaixml(origdesc_el):
    provenances = [{'harvest_date': origdesc_el.get('harvestDate'),
                    'altered': origdesc_el.get('altered') == 'true',
                    'direct': False,
                    'base_url': ''.join(origdesc_el.find('./oai_p:baseURL', OAI_NS).itertext()),
                    'identifier': ''.join(origdesc_el.find('./oai_p:identifier', OAI_NS).itertext()),
                    'datestamp': ''.join(origdesc_el.find('./oai_p:datestamp', OAI_NS).itertext()),
                    'metadata_namespace': ''.join(origdesc_el.find('./oai_p:metadataNamespace', OAI_NS).itertext())}]
    nested_origdesc_el = origdesc_el.find('./oai_p:originDescription', OAI_NS)
    if nested_origdesc_el:
        provenances.extend(_indirect_provenances_from_oaixml(nested_origdesc_el))
    return provenances


class ProvenanceInfo:

    def __init__(self, root_element, metadata_namespace):
        self._root_element = root_element
        self._metadata_namespace = metadata_namespace
        self._direct_provenance = {
            'harvest_date': datetime_to_datestamp(datetime_now()),
            'altered': True, 'direct': True,
            'metadata_namespace': metadata_namespace,
            'base_url': ''.join(self._root_element.find('./oai:request', OAI_NS).itertext()),
            'identifier': ''.join(self._root_element.find(
                './oai:GetRecord/oai:record/oai:header/oai:identifier', OAI_NS).itertext()),
            'datestamp': ''.join(self._root_element.find(
                './oai:GetRecord/oai:record/oai:header/oai:datestamp', OAI_NS).itertext())
        }

    @property
    def base_url(self):
        return self._direct_provenance['base_url']

    @property
    def identifier(self):
        return self._direct_provenance['identifier']

    def full(self):
        provenances = [self._direct_provenance]
        prov_el = self._root_element.find('./oai:GetRecord/oai:record/oai:about/oai_p:provenance', OAI_NS)
        if prov_el:
            provenances.extend(_indirect_provenances_from_oaixml(prov_el.find('./oai_p:originDescription', OAI_NS)))
        return provenances


def _expect_oai_pmh_root(root_element):
    exp_root_tag = '{http://www.openarchives.org/OAI/2.0/}OAI-PMH'
    if root_element.tag != exp_root_tag:
        raise ddi.UnknownXMLRoot(exp_root_tag, root_element.tag)


def _add_provenances(obj, getter):
    for prov in getter():
        obj._provenance.add_value(prov['harvest_date'],
                                  altered=prov['altered'],
                                  base_url=prov['base_url'],
                                  identifier=prov['identifier'],
                                  datestamp=prov['datestamp'],
                                  direct=prov['direct'],
                                  metadata_namespace=prov['metadata_namespace'])


def _aggregator_study_number(base_url, identifier):
    # Join base_url + identifier with two underscores and use URL quoting
    return quote_plus('__'.join([base_url, identifier]))


def _aggregator_parser_factory(baseclass):

    class DynamicAggregatorBase(baseclass):
        """Dynamic class to minimize duplicated code blocks."""

        _study_cls = Study

        def _ddic_init(self, root_element, ddi_ns):
            _expect_oai_pmh_root(root_element)
            namespaces = dict(**ddi_ns, oai=OAI_NS['oai'])
            ddi_root = root_element.find('./oai:GetRecord/oai:record/oai:metadata/ddi:codeBook', namespaces)
            if ddi_root is None:
                raise ddi.UnknownXMLRoot('{%s}codeBook' % (namespaces['ddi'],))
            self._provenance_info = ProvenanceInfo(root_element, namespaces['ddi'])
            return ddi_root

        def _parse_study_number(self):
            self.study_number = _aggregator_study_number(self._provenance_info.base_url,
                                                         self._provenance_info.identifier)

        @property
        def studies(self):
            for study in super().studies:
                _add_provenances(study, self._provenance_info.full)
                yield study

    return DynamicAggregatorBase


class DDI122NesstarRecordParser(_aggregator_parser_factory(ddi.DDI122NesstarRecordParser)):
    """Parse OAI-PMH record containing DDI122 Nesstar metadata
    and map it to CDCAGG records."""

    def __init__(self, root_element):
        super().__init__(self._ddic_init(root_element,
                                         {'ddi': 'http://www.icpsr.umich.edu/DDI'}))


class DDI25RecordParser(_aggregator_parser_factory(ddi.DDI25RecordParser)):
    """Parse OAI-PMH record containing DDI2.5 metadata
    and map it to CDCAGG records."""

    def __init__(self, root_element):
        super().__init__(self._ddic_init(root_element,
                                         {'ddi': 'ddi:codebook:2_5'}))


class DDI31RecordParser(_aggregator_parser_factory(ddi.DDI31RecordParser)):
    """Parse OAI-PMH record containing DDI3.1 metadata
    and map it to CDCAGG records."""

    def __init__(self, root_element):
        _expect_oai_pmh_root(root_element)
        _ns = {'oai': 'http://www.openarchives.org/OAI/2.0/',
               's': 'ddi:studyunit:3_1',
               'ddi': 'ddi:instance:3_1'}
        ddi_root = None
        ddi_instance_root = root_element.find(
            './oai:GetRecord/oai:record/oai:metadata/ddi:DDIInstance', _ns)
        if ddi_instance_root is not None:
            ddi_root = ddi_instance_root
            metadata_namespace = _ns['ddi']
        else:
            ddi_root = root_element.find(
                './oai:GetRecord/oai:record/oai:metadata/s:StudyUnit', _ns)
            metadata_namespace = _ns['s']
        if ddi_root is None:
            raise ddi.UnknownXMLRoot('{%s}DDIInstance or {%s}StudyUnit' % (_ns['ddi'], _ns['s']))
        self._provenance_info = ProvenanceInfo(root_element, metadata_namespace)
        super().__init__(ddi_root)
