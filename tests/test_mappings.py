# Copyright CESSDA ERIC 2021
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

from unittest import (
    TestCase,
    mock
)
from xml.etree import ElementTree
from kuha_common.document_store.mappings.exceptions import UnknownXMLRoot
from cdcagg_common import mappings


def _valid_root(metadata='', base_url='', identifier='', datestamp='', about=''):
    metadata = metadata or ''
    base_url = base_url or ''
    identifier = identifier or ''
    datestamp = datestamp or ''
    return ('<OAI-PMH xmlns="http://www.openarchives.org/OAI/2.0/" '
            'xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" '
            'xsi:schemaLocation="http://www.openarchives.org/OAI/2.0/ '
            'http://www.openarchives.org/OAI/2.0/OAI-PMH.xsd">'
            '<request>' + base_url + '</request>'
            '<GetRecord><record><header>'
            '<identifier>' + identifier + '</identifier>'
            '<datestamp>' + datestamp  + '</datestamp></header>'
            '<metadata>' + metadata + '</metadata>' + about +
            '</record></GetRecord>'
            '</OAI-PMH>')


def _invalid_root(inner_xml=''):
    return ('<invalid_root>' + inner_xml + '</invalid_root>')


class TestProvenanceInfo(TestCase):

    def test_gets_direct_provenance_info(self):
        root_element = ElementTree.fromstring(_valid_root(
            base_url='http://some.base.url', identifier='some_identifier',
            datestamp='2015-01-20T13:32:15+0000'))
        prov = mappings.ProvenanceInfo(root_element, 'somenamespace')
        rval = prov.full()
        self.assertEqual(len(rval), 1)
        prov = rval.pop()
        self.assertEqual(prov['base_url'], 'http://some.base.url')
        self.assertEqual(prov['identifier'], 'some_identifier')
        self.assertEqual(prov['datestamp'], '2015-01-20T13:32:15+0000')
        self.assertEqual(prov['altered'], True)
        self.assertEqual(prov['direct'], True)
        self.assertEqual(prov['metadata_namespace'], 'somenamespace')

    @mock.patch.object(mappings, 'datetime_to_datestamp')
    def test_gets_provenance_info(self, mock_datetime_to_datestamp):
        about_xml = ('<about><provenance xmlns="http://www.openarchives.org/OAI/2.0/provenance" '
                     'xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" '
                     'xsi:schemaLocation="http://www.openarchives.org/OAI/2.0/provenance '
                     'http://www.openarchives.org/OAI/2.0/provenance.xsd">'
                     # Direct begins here
                     '<originDescription harvestDate="2002-02-02T14:10:02Z" altered="true">'
                     '<baseURL>http://the.oa.org</baseURL>'
                     '<identifier>oai:r2.org:klik001</identifier>'
                     '<datestamp>2002-01-01</datestamp>'
                     '<metadataNamespace>http://www.openarchives.org/OAI/2.0/oai_dc/</metadataNamespace>'
                     # Nested begins here
                     '<originDescription harvestDate="2002-01-01T11:10:01Z" altered="false">'
                     '<baseURL>http://some.oa.org</baseURL>'
                     '<identifier>oai:r2.org:klik002</identifier>'
                     '<datestamp>2001-01-01</datestamp>'
                     '<metadataNamespace>http://www.openarchives.org/OAI/2.0/oai_dc2/</metadataNamespace>'
                     '</originDescription></originDescription>'
                     '</provenance></about>')
        root_element = ElementTree.fromstring(_valid_root(
            base_url='http://other.base.url', identifier='other_identifier',
            datestamp='2016-01-20T13:32:15+0000', about=about_xml))
        prov_info = mappings.ProvenanceInfo(root_element, 'othernamespace')
        rval = prov_info.full()
        self.assertEqual(len(rval), 3)
        exp_provs = [
            {'base_url': 'http://other.base.url',
             'identifier': 'other_identifier',
             'datestamp': '2016-01-20T13:32:15+0000',
             'altered': True,
             'direct': True,
             'harvest_date': mock_datetime_to_datestamp.return_value,
             'metadata_namespace': 'othernamespace'},
            {'base_url': 'http://the.oa.org',
             'identifier': 'oai:r2.org:klik001',
             'datestamp': '2002-01-01',
             'altered': True,
             'direct': False,
             'harvest_date': '2002-02-02T14:10:02Z',
             'metadata_namespace': 'http://www.openarchives.org/OAI/2.0/oai_dc/'},
            {'base_url': 'http://some.oa.org',
             'identifier': 'oai:r2.org:klik002',
             'datestamp': '2001-01-01',
             'altered': False,
             'direct': False,
             'harvest_date': '2002-01-01T11:10:01Z',
             'metadata_namespace': 'http://www.openarchives.org/OAI/2.0/oai_dc2/'}
        ]
        for index, prov in enumerate(rval):
            self.assertEqual(prov, exp_provs[index])


class TestExpectOAIPMHRoot(TestCase):

    def test_raises_UnknownXMLRoot_for_invalid_root_element(self):
        root_element = ElementTree.fromstring(_invalid_root())
        with self.assertRaises(UnknownXMLRoot):
            mappings._expect_oai_pmh_root(root_element)

    def test_does_not_raise_for_valid_root_element(self):
        root_element = ElementTree.fromstring(_valid_root())
        # If this does not raise, we're good.
        mappings._expect_oai_pmh_root(root_element)


class _Wrapper:

    class RecordParserTestBase(TestCase):

        def test_raises_UnknownXMLRoot_for_invalid_root_element(self):
            with self.assertRaises(UnknownXMLRoot):
                self.ParserClass.from_string(self._valid_md)

        def test_raises_UnknownXMLRoot_for_invalid_ddi_root(self):
            with self.assertRaises(UnknownXMLRoot):
                self.ParserClass.from_string(_valid_root(metadata=self._invalid_md))

        def test_returns_studies(self):
            studies = list(self.ParserClass.from_string(_valid_root(metadata=self._valid_study,
                                                                    base_url='some.base.url',
                                                                    identifier='some/oai/id')).studies)
            self.assertEqual(len(studies), 1)
            study = studies.pop()
            self.assertEqual(study.study_number.get_value(), 'some.base.url__some2Foai2Fid')
            self.assertEqual(study.study_titles[0].get_value(), self._valid_study_title)
            self.assertEqual(study.identifiers[0].get_value(), self._valid_study_idno)

        @mock.patch.object(mappings, 'datetime_to_datestamp')
        def test_returned_study_contain_proper_provenance(self, mock_datetime_to_datestamp):
            study = list(self.ParserClass.from_string(_valid_root(
                metadata=self._valid_study,
                base_url='http://some.base.url',
                identifier='someoaiidentifier',
                datestamp='2000-01-01'
            )).studies).pop()
            self.assertEqual(
                study._provenance.export_dict(),
                {'_provenance': [
                    {'altered': True,
                     'base_url': 'http://some.base.url',
                     'identifier': 'someoaiidentifier',
                     'datestamp': '2000-01-01',
                     'direct': True,
                     'metadata_namespace': self._mdns,
                     'harvest_date': mock_datetime_to_datestamp.return_value}]})

        def test_does_not_raise_for_valid_root_element(self):
            self.ParserClass.from_string(_valid_root(metadata=self._valid_md))


class TestDDI122RecordParser(_Wrapper.RecordParserTestBase):

    _mdns = 'http://www.icpsr.umich.edu/DDI'
    _valid_md = '<codeBook xmlns="http://www.icpsr.umich.edu/DDI"></codeBook>'
    _invalid_md = '<codeBook></codeBook>'
    _valid_study_idno = 'some idno'
    _valid_study_title = 'some study'
    _valid_study = ('<codeBook xmlns="http://www.icpsr.umich.edu/DDI">'
                    '<stdyDscr xmlns=""><citation><titlStmt>'
                    '<titl>some study</titl>'
                    '<IDNo>some idno</IDNo>'
                    '</titlStmt></citation></stdyDscr></codeBook>')
    ParserClass = mappings.DDI122NesstarRecordParser


class TestDDI25RecordParser(_Wrapper.RecordParserTestBase):

    _mdns = 'ddi:codebook:2_5'
    _valid_md = ('<codeBook xmlns="ddi:codebook:2_5" version="2.5" '
                 'xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" '
                 'xsi:schemaLocation="ddi:codebook:2_5 http://www.ddialliance.org/'
                 'Specification/DDI-Codebook/2.5/XMLSchema/codebook.xsd">'
                 '</codeBook>')
    _invalid_md = ('<codeBook xmlns="codebook:2_5" version="2.5" '
                   'xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" '
                   'xsi:schemaLocation="ddi:codebook:2_5 http://www.ddialliance.org/'
                   'Specification/DDI-Codebook/2.5/XMLSchema/codebook.xsd">'
                   '</codeBook>')
    _valid_study_idno = 'other idno'
    _valid_study_title = 'other study'
    _valid_study = ('<codeBook xmlns="ddi:codebook:2_5" version="2.5" '
                    'xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" '
                    'xsi:schemaLocation="ddi:codebook:2_5 http://www.ddialliance.org/'
                    'Specification/DDI-Codebook/2.5/XMLSchema/codebook.xsd">'
                    '<stdyDscr><citation><titlStmt>'
                    '<titl>other study</titl>'
                    '<IDNo>other idno</IDNo>'
                    '</titlStmt></citation></stdyDscr>'
                    '</codeBook>')
    ParserClass = mappings.DDI25RecordParser


class TestDDI31RecordParser(_Wrapper.RecordParserTestBase):

    _mdns = 'ddi:instance:3_1'
    _valid_md = ('<ddi:DDIInstance xmlns:m2="ddi:physicaldataproduct_ncube_tabular:3_1" xmlns:r="ddi:reusable:3_1" '
                 'xmlns:m3="ddi:physicaldataproduct_ncube_inline:3_1" '
                 'xmlns:s="ddi:studyunit:3_1" '
                 'xmlns:dce="ddi:dcelements:3_1" '
                 'xmlns:pi="ddi:physicalinstance:3_1" '
                 'xmlns:g="ddi:group:3_1" '
                 'xmlns:dc="http://purl.org/dc/elements/1.1/" '
                 'xmlns:xs="http://www.w3.org/2001/XMLSchema" '
                 'xmlns:m4="ddi:physicaldataproduct_proprietary:3_1" '
                 'xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" '
                 'xmlns:ddi="ddi:instance:3_1" '
                 'xmlns:a="ddi:archive:3_1" '
                 'xmlns:cm="ddi:comparative:3_1" '
                 'xmlns:pr="ddi:ddiprofile:3_1" '
                 'xmlns:l="ddi:logicalproduct:3_1" '
                 'xmlns:c="ddi:conceptualcomponent:3_1" '
                 'xmlns:ds="ddi:dataset:3_1" '
                 'xmlns:d="ddi:datacollection:3_1" '
                 'xmlns:xhtml="http://www.w3.org/1999/xhtml" '
                 'xmlns:m1="ddi:physicaldataproduct_ncube_normal:3_1" '
                 'xmlns:p="ddi:physicaldataproduct:3_1" '
                 'xsi:schemaLocation="ddi:instance:3_1 http://www.ddialliance.org/Specification/DDI-Lifecycle/3.1/'
                 'XMLSchema/instance.xsd">'
                 '<s:StudyUnit></s:StudyUnit>'
                 '</ddi:DDIInstance>')
    _invalid_md = ('<ddi:DDIInstance xmlns:m2="ddi:physicaldataproduct_ncube_tabular:3_1" xmlns:r="ddi:reusable:3_1" '
                   'xmlns:m3="ddi:physicaldataproduct_ncube_inline:3_1" '
                   'xmlns:s="ddi:studyunit:3_1" '
                   'xmlns:dce="ddi:dcelements:3_1" '
                   'xmlns:pi="ddi:physicalinstance:3_1" '
                   'xmlns:g="ddi:group:3_1" '
                   'xmlns:dc="http://purl.org/dc/elements/1.1/" '
                   'xmlns:xs="http://www.w3.org/2001/XMLSchema" '
                   'xmlns:m4="ddi:physicaldataproduct_proprietary:3_1" '
                   'xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" '
                   'xmlns:ddi="instance:3_1" '
                   'xmlns:a="ddi:archive:3_1" '
                   'xmlns:cm="ddi:comparative:3_1" '
                   'xmlns:pr="ddi:ddiprofile:3_1" '
                   'xmlns:l="ddi:logicalproduct:3_1" '
                   'xmlns:c="ddi:conceptualcomponent:3_1" '
                   'xmlns:ds="ddi:dataset:3_1" '
                   'xmlns:d="ddi:datacollection:3_1" '
                   'xmlns:xhtml="http://www.w3.org/1999/xhtml" '
                   'xmlns:m1="ddi:physicaldataproduct_ncube_normal:3_1" '
                   'xmlns:p="ddi:physicaldataproduct:3_1" '
                   'xsi:schemaLocation="ddi:instance:3_1 http://www.ddialliance.org/Specification/DDI-Lifecycle/3.1/'
                   'XMLSchema/instance.xsd">'
                   '<s:StudyUnit></s:StudyUnit>'
                   '</ddi:DDIInstance>')
    _valid_study_idno = 'yet another idno'
    _valid_study_title = 'yet another study'
    _valid_study = ('<ddi:DDIInstance xmlns:m2="ddi:physicaldataproduct_ncube_tabular:3_1" xmlns:r="ddi:reusable:3_1" '
                    'xmlns:m3="ddi:physicaldataproduct_ncube_inline:3_1" '
                    'xmlns:s="ddi:studyunit:3_1" '
                    'xmlns:dce="ddi:dcelements:3_1" '
                    'xmlns:pi="ddi:physicalinstance:3_1" '
                    'xmlns:g="ddi:group:3_1" '
                    'xmlns:dc="http://purl.org/dc/elements/1.1/" '
                    'xmlns:xs="http://www.w3.org/2001/XMLSchema" '
                    'xmlns:m4="ddi:physicaldataproduct_proprietary:3_1" '
                    'xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" '
                    'xmlns:ddi="ddi:instance:3_1" '
                    'xmlns:a="ddi:archive:3_1" '
                    'xmlns:cm="ddi:comparative:3_1" '
                    'xmlns:pr="ddi:ddiprofile:3_1" '
                    'xmlns:l="ddi:logicalproduct:3_1" '
                    'xmlns:c="ddi:conceptualcomponent:3_1" '
                    'xmlns:ds="ddi:dataset:3_1" '
                    'xmlns:d="ddi:datacollection:3_1" '
                    'xmlns:xhtml="http://www.w3.org/1999/xhtml" '
                    'xmlns:m1="ddi:physicaldataproduct_ncube_normal:3_1" '
                    'xmlns:p="ddi:physicaldataproduct:3_1" '
                    'xsi:schemaLocation="ddi:instance:3_1 http://www.ddialliance.org/Specification/DDI-Lifecycle/3.1/'
                    'XMLSchema/instance.xsd">'
                    '<s:StudyUnit><r:Citation>'
                    '<r:Title>yet another study</r:Title>'
                    '</r:Citation><a:Archive><a:ArchiveSpecific><a:Collection>'
                    '<a:CallNumber>yet another idno</a:CallNumber>'
                    '</a:Collection></a:ArchiveSpecific></a:Archive></s:StudyUnit>'
                    '</ddi:DDIInstance>')
    ParserClass = mappings.DDI31RecordParser
