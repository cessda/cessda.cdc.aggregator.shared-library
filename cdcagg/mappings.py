from kuha_common.document_store.mappings import ddi
from kuha_common.document_store.records import datetime_now
from cdcagg.records import (
    Study
)

OAI_NS = {'oai': 'http://www.openarchives.org/OAI/2.0/'}


def provenance_getter(root_element):
    def get_provenance_infos():
        # TODO get existing provenance info, with direct=False
        # TODO metadata_namespace
        return [{'harvest_date': datetime_now(),
                 'altered': True, 'direct': True,
                 'metadata_namespace': 'somenamespace',  # TODO
                 'base_url': ''.join(root_element.find('./oai:request', OAI_NS).itertext()),
                 'identifier': ''.join(root_element.find(
                     './oai:GetRecord/oai:record/oai:header/oai:identifier', OAI_NS).itertext()),
                 'datestamp': ''.join(root_element.find(
                     './oai:GetRecord/oai:record/oai:header/oai:datestamp', OAI_NS).itertext())}]
    return get_provenance_infos


class DDI122RecordParser(ddi.DDI122RecordParser):

    _study_cls = Study


class DDI25RecordParser(ddi.DDI25RecordParser):

    _study_cls = Study

    def __init__(self, root_element):
        exp_root_tag = '{http://www.openarchives.org/OAI/2.0/}OAI-PMH'
        if root_element.tag != exp_root_tag:
            raise ddi.UnknownXMLRoot(exp_root_tag, root_element.tag)
        ddi_root = root_element.find('./oai:GetRecord/oai:record/oai:metadata/ddi:codeBook',
                                     {'oai': 'http://www.openarchives.org/OAI/2.0/',
                                      'ddi': 'ddi:codebook:2_5'})
        if ddi_root is None:
            raise ddi.UnknownXMLRoot('{ddi:codebook:2_5}codeBook')
        self._provenance_getter = provenance_getter(root_element)
        super().__init__(ddi_root)

    @property
    def studies(self):
        for study in super().studies:
            for provenance in self._provenance_getter():
                study._provenance.add_value(provenance['harvest_date'],
                                            altered=provenance['altered'],
                                            base_url=provenance['base_url'],
                                            identifier=provenance['identifier'],
                                            datestamp=provenance['datestamp'],
                                            direct=provenance['direct'],
                                            metadata_namespace=provenance['metadata_namespace'])
            yield study


class DDI31RecordParser(ddi.DDI31RecordParser):

    _study_cls = Study

    def __init__(self, root_element):
        exp_root_tag = '{http://www.openarchives.org/OAI/2.0/}OAI-PMH'
        if root_element.tag != exp_root_tag:
            raise ddi.UnknownXMLRoot(exp_root_tag, root_element.tag)
        ddi_root = root_element.find(
            './oai:GetRecord/oai:record/oai:metadata/ddi:DDIInstance',
            {'oai': 'http://www.openarchives.org/OAI/2.0/',
             'ddi': 'ddi:instance:3_1'})
        if ddi_root is None:
            raise ddi.UnknownXMLRoot('{ddi:instance:3_1}DDIInstance')
        self._provenance_getter = provenance_getter(root_element)
        super().__init__(ddi_root)

    @property
    def studies(self):
        for study in super().studies:
            for provenance in self._provenance_getter():
                study._provenance.add_value(provenance['harvest_date'],
                                            altered=provenance['altered'],
                                            base_url=provenance['base_url'],
                                            identifier=provenance['identifier'],
                                            datestamp=provenance['datestamp'],
                                            direct=provenance['direct'],
                                            metadata_namespace=provenance['metadata_namespace'])
            yield study
