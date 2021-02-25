from kuha_common.document_store.mappings import ddi
from kuha_common.document_store.records import datetime_now
from cdc_oai_aggregator.records import (
    Study
)

OAI_NS = {'oai': 'http://www.openarchives.org/OAI/2.0/'}


def get_provenance_info(root_element):
    return {'harvest_date': datetime_now(),
            'altered': True,
            'base_url': ''.join(root_element.find('./oai:request', OAI_NS).itertext()),
            'identifier': ''.join(root_element.find(
                './oai:GetRecord/oai:record/oai:header/oai:identifier', OAI_NS).itertext()),
            'datestamp': ''.join(root_element.find(
                './oai:GetRecord/oai:record/oai:header/oai:datestamp', OAI_NS).itertext())}


class DDI122RecordParser(ddi.DDI122RecordParser):

    _study_cls = Study


class DDI25RecordParser(ddi.DDI25RecordParser):

    _study_cls = Study

    def __init__(self, root_element):
        exp_root_tag = '{http://www.openarchives.org/OAI/2.0/}OAI-PMH'
        if root_element.tag != exp_root_tag:
            raise ddi.UnknownXMLRoot(exp_root_tag, root_element.tag)
        self._provenance_info = get_provenance_info(root_element)
        super().__init__(root_element.find(
            './oai:GetRecord/oai:record/oai:metadata/ddi:codeBook',
            {'oai': 'http://www.openarchives.org/OAI/2.0/',
             'ddi': 'ddi:codebook:2_5'}))


if __name__ == '__main__':
    import sys
    import os.path
    usage = 'python -m cdc_oai_aggregator.mappings [in_file]'
    if len(sys.argv) != 2:
        print('ERROR: Invalid number or arguments')
        print(usage)
    filepath = sys.argv[-1]
    if not os.path.isabs(filepath):
        filepath = os.path.abspath(filepath)
    parser = DDI25RecordParser.from_file(filepath)
    s = next(parser.studies)
    import code; code.interact(local=locals())
