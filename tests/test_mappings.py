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

        def test_raises_UnknownXMLRoot_when_no_oai_metadata_element(self):
            with self.assertRaises(UnknownXMLRoot):
                self.ParserClass.from_string(
                    ('<OAI-PMH xmlns="http://www.openarchives.org/OAI/2.0/" '
                     'xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" '
                     'xsi:schemaLocation="http://www.openarchives.org/OAI/2.0/ '
                     'http://www.openarchives.org/OAI/2.0/OAI-PMH.xsd">'
                     '<request>some_base_url</request>'
                     '<GetRecord><record><header>'
                     '<identifier>identifier</identifier>'
                     '<datestamp>datestamp</datestamp></header>'
                     '</record></GetRecord></OAI-PMH>'))

        def test_returns_studies(self):
            studies = list(self.ParserClass.from_string(_valid_root(metadata=self._valid_study,
                                                                    base_url='some.base.url',
                                                                    identifier='some/oai/id')).studies)
            self.assertEqual(len(studies), 1)
            study = studies.pop()
            self.assertEqual(study.study_number.get_value(), 'some.base.url__some2Foai2Fid')
            self.assertEqual(study.study_titles[0].get_value(), self._valid_study_title)
            self.assertEqual(study.identifiers[0].get_value(), self._valid_study_idno)

        def test_generates_proper_aggregator_identifier(self):
            """Aggregator identifier is generated by joining OAI-PMH
            BaseURL and OAI Identifier with a hyphen (-) and hashing
            with sha256. Its value is the hexadecimal notation of the
            hash.

            Tests implementation of
            https://github.com/cessda/cessda.cdc.aggregator.shared-library/issues/27
            """
            studies = list(self.ParserClass.from_string(
                _valid_root(metadata=self._valid_md,
                            base_url='https://some.url/oai',
                            identifier='oai:some.domain:local_identifier')).studies)
            self.assertEqual(len(studies), 1)
            study = studies.pop()
            # Asserted value generated manually by:
            # >>> from hashlib import sha256
            # >>> sha256('https://some.url/oai-oai:some.domain:local_identifier'.encode('utf8')).hexdigest()
            # '8c70c7fd65e84fdf7cc08690ebbf944605690f7e0b7ebcb995d6c35c9c0185fc'
            self.assertEqual(study._aggregator_identifier.get_value(),
                             '8c70c7fd65e84fdf7cc08690ebbf944605690f7e0b7ebcb995d6c35c9c0185fc')

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

        def test_returned_study_countains_proper_direct_base_url(self):
            study = list(self.ParserClass.from_string(_valid_root(
                metadata=self._valid_study,
                base_url='http://some.base.url',
                identifier='someoaiidentifier',
                datestamp='2000-01-01'
            )).studies).pop()
            self.assertEqual(study._direct_base_url.export_dict(),
                             {'_direct_base_url': 'http://some.base.url'})

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


class TestDDI32RecordParser(_Wrapper.RecordParserTestBase):
    _mdns = 'ddi:instance:3_2'
    _valid_md = ('<ddi:DDIInstance xmlns:ddi="ddi:instance:3_2" '
                 'xmlns:s="ddi:studyunit:3_2" '
                 'xmlns:pd="ddi:physicaldataproduct:3_2" '
                 'xmlns:pi="ddi:physicalinstance:3_2" '
                 'xmlns:c="ddi:conceptualcomponent:3_2" '
                 'xmlns:l="ddi:logicalproduct:3_2" '
                 'xmlns:r="ddi:reusable:3_2" '
                 'xmlns:dc="ddi:datacollection:3_2" '
                 'xmlns:a="ddi:archive:3_2" '
                 'xmlns:g="ddi:group:3_2" '
                 'xmlns:xhtml="http://www.w3.org/1999/xhtml" '
                 'xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" '
                 'xsi:schemaLocation="ddi:instance:3_2 http://www.ddialliance.org/Specification/DDI-Lifecycle/'
                 '3.2/XMLSchema/instance.xsd">'
                 '<s:StudyUnit></s:StudyUnit>'
                 '</ddi:DDIInstance>')
    _invalid_md = ('<ddi:DDIInstance xmlns:ddi="ddi:instance:3" '
                   'xmlns:s="ddi:studyunit:3_2" '
                   'xmlns:pd="ddi:physicaldataproduct:3_2" '
                   'xmlns:pi="ddi:physicalinstance:3_2" '
                   'xmlns:c="ddi:conceptualcomponent:3_2" '
                   'xmlns:l="ddi:logicalproduct:3_2" '
                   'xmlns:r="ddi:reusable:3_2" '
                   'xmlns:dc="ddi:datacollection:3_2" '
                   'xmlns:a="ddi:archive:3_2" '
                   'xmlns:g="ddi:group:3_2" '
                   'xmlns:xhtml="http://www.w3.org/1999/xhtml" '
                   'xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" '
                   'xsi:schemaLocation="ddi:instance:3_2 http://www.ddialliance.org/Specification/DDI-Lifecycle/'
                   '3.2/XMLSchema/instance.xsd">'
                   '<s:StudyUnit></s:StudyUnit>'
                   '</ddi:DDIInstance>')
    _valid_study = ('<ddi:DDIInstance xmlns:ddi="ddi:instance:3_2" '
                    'xmlns:s="ddi:studyunit:3_2" '
                    'xmlns:pd="ddi:physicaldataproduct:3_2" '
                    'xmlns:pi="ddi:physicalinstance:3_2" '
                    'xmlns:c="ddi:conceptualcomponent:3_2" '
                    'xmlns:l="ddi:logicalproduct:3_2" '
                    'xmlns:r="ddi:reusable:3_2" '
                    'xmlns:dc="ddi:datacollection:3_2" '
                    'xmlns:a="ddi:archive:3_2" '
                    'xmlns:g="ddi:group:3_2" '
                    'xmlns:xhtml="http://www.w3.org/1999/xhtml" '
                    'xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" '
                    'xsi:schemaLocation="ddi:instance:3_2 http://www.ddialliance.org/Specification/DDI-Lifecycle/'
                    '3.2/XMLSchema/instance.xsd">'
                    "<s:StudyUnit><r:UserID typeOfUserID='StudyNumber'>id for ddi32</r:UserID>"
                    '<r:Citation><r:Title><r:String>'
                    'title for ddi32'
                    '</r:String></r:Title></r:Citation></s:StudyUnit>'
                    '</ddi:DDIInstance>')
    _valid_study_title = 'title for ddi32'
    _valid_study_idno = 'id for ddi32'
    ParserClass = mappings.DDI32RecordParser

    def test_accepts_FragmentInstance(self):
        """DDI32 can be wrapped in FragmentInstance"""
        metadata = ('<FragmentInstance xmlns="ddi:instance:3_2" xmlns:r="ddi:reusable:3_2">'
                    '<TopLevelReference><r:URN>urn:ddi:some_agency:some_id:1</r:URN>'
                    '<r:TypeOfObject>StudyUnit</r:TypeOfObject></TopLevelReference>'
                    '<Fragment><StudyUnit xmlns="ddi:studyunit:3_2">'
                    '<r:Agency>some_agency</r:Agency>'
                    '<r:ID>some_id</r:ID>'
                    '<r:Version>1</r:Version>'
                    '<r:Citation><r:Title><r:String>some title</r:String></r:Title></r:Citation>'
                    '</StudyUnit></Fragment></FragmentInstance>')
        studies = list(self.ParserClass.from_string(_valid_root(metadata=metadata,
                                                                base_url='some.base.url',
                                                                identifier='some/oai/id')).studies)
        self.assertEqual(len(studies), 1)
        study = studies.pop()
        self.assertEqual(study.study_number.get_value(), 'some.base.url__some2Foai2Fid')
        self.assertEqual(study.study_titles[0].get_value(), 'some title')
        self.assertEqual(study._provenance[0].attr_metadata_namespace.get_value(), 'ddi:instance:3_2')


class TestDDI33RecordParser(_Wrapper.RecordParserTestBase):

    _mdns = 'ddi:instance:3_3'
    _ddi_instance_root = ('<ddi:DDIInstance xmlns:ddi="ddi:instance:3_3" '
                          'xmlns:s="ddi:studyunit:3_3" '
                          'xmlns:pd="ddi:physicaldataproduct:3_3" '
                          'xmlns:pi="ddi:physicalinstance:3_3" '
                          'xmlns:c="ddi:conceptualcomponent:3_3" '
                          'xmlns:l="ddi:logicalproduct:3_3" '
                          'xmlns:r="ddi:reusable:3_3" '
                          'xmlns:dc="ddi:datacollection:3_3" '
                          'xmlns:a="ddi:archive:3_3" '
                          'xmlns:g="ddi:group:3_3" '
                          'xmlns:xhtml="http://www.w3.org/1999/xhtml" '
                          'xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" '
                          'xsi:schemaLocation="ddi:instance:3_1 '
                          'http://www.ddialliance.org/Specification/DDI-Lifecycle/'
                          '3.3/XMLSchema/instance.xsd">')
    _valid_md = (_ddi_instance_root +
                 '<s:StudyUnit></s:StudyUnit>'
                 '</ddi:DDIInstance>')
    _invalid_md = ('<ddi:DDIInstance xmlns:ddi="ddi:instance:3" '
                   'xmlns:s="ddi:studyunit:3_3" '
                   'xmlns:pd="ddi:physicaldataproduct:3_3" '
                   'xmlns:pi="ddi:physicalinstance:3_3" '
                   'xmlns:c="ddi:conceptualcomponent:3_3" '
                   'xmlns:l="ddi:logicalproduct:3_3" '
                   'xmlns:r="ddi:reusable:3_3" '
                   'xmlns:dc="ddi:datacollection:3_3" '
                   'xmlns:a="ddi:archive:3_3" '
                   'xmlns:g="ddi:group:3_3" '
                   'xmlns:xhtml="http://www.w3.org/1999/xhtml" '
                   'xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" '
                   'xsi:schemaLocation="ddi:instance:3_1 http://www.ddialliance.org/Specification/DDI-Lifecycle/'
                   '3.3/XMLSchema/instance.xsd">'
                   '<s:StudyUnit></s:StudyUnit>'
                   '</ddi:DDIInstance>')
    _valid_study_idno = 'idno for ddi33'
    _valid_study_title = 'title for ddi33'
    _valid_study = (_ddi_instance_root +
                    '<s:StudyUnit><r:Citation><r:Title><r:String>'
                    'title for ddi33'
                    '</r:String></r:Title></r:Citation>'
                    '<a:Archive><a:ArchiveSpecific><a:Collection>'
                    '<a:CallNumber>idno for ddi33</a:CallNumber>'
                    '</a:Collection></a:ArchiveSpecific></a:Archive></s:StudyUnit>'
                    '</ddi:DDIInstance>')
    ParserClass = mappings.DDI33RecordParser

    def test_accepts_FragmentInstance(self):
        """DDI33 can be wrapped in FragmentInstance root element."""
        metadata = ('<FragmentInstance xmlns="ddi:instance:3_3" xmlns:r="ddi:reusable:3_3">'
                    '<TopLevelReference><r:URN>urn:ddi:some_agency:some_id:1</r:URN>'
                    '<r:TypeOfObject>StudyUnit</r:TypeOfObject></TopLevelReference>'
                    '<Fragment><StudyUnit xmlns="ddi:studyunit:3_3">'
                    '<r:Agency>some_agency</r:Agency>'
                    '<r:ID>some_id</r:ID>'
                    '<r:Version>1</r:Version>'
                    '<r:Citation><r:Title><r:String>some title</r:String></r:Title></r:Citation>'
                    '</StudyUnit></Fragment></FragmentInstance>')
        studies = list(self.ParserClass.from_string(_valid_root(metadata=metadata,
                                                                base_url='some.base.url',
                                                                identifier='some/oai/id')).studies)
        self.assertEqual(len(studies), 1)
        study = studies.pop()
        self.assertEqual(study.study_number.get_value(), 'some.base.url__some2Foai2Fid')
        self.assertEqual(study.study_titles[0].get_value(), 'some title')
        self.assertEqual(study._provenance[0].attr_metadata_namespace.get_value(), 'ddi:instance:3_3')

    def test_primary_identifier_from_UserID(self):
        """Make sure UserID is now the primary source for Study.identifiers

        Issue at github:
        https://github.com/cessda/cessda.cdc.aggregator.shared-library/issues/52"""
        studies = list(self.ParserClass.from_string(_valid_root(
            metadata=self._ddi_instance_root +
            '<s:StudyUnit><r:UserID typeOfUserID="StudyNumber">identifier</r:UserID>'
            '<a:Archive><a:ArchiveSpecific><a:Collection>'
            '<a:CallNumber>idno for ddi33</a:CallNumber>'
            '</a:Collection></a:ArchiveSpecific></a:Archive>'
            '</s:StudyUnit></ddi:DDIInstance>',
            base_url='some.base',
            identifier='oai_rec_1'
        )).studies)
        self.assertEqual(len(studies), 1)
        study = studies[0]
        self.assertEqual(len(study.identifiers), 1)
        self.assertEqual(study.identifiers[0].get_value(), 'identifier')

    def test_primary_identifier_not_from_UserID(self):
        """Make sure UserID is not read into identifiers if @typeOfUserID is incorrect

        Issue at github:
        https://github.com/cessda/cessda.cdc.aggregator.shared-library/issues/52"""
        studies = list(self.ParserClass.from_string(_valid_root(
            metadata=self._ddi_instance_root +
            '<s:StudyUnit><r:UserID typeOfUserID="incorrect">identifier</r:UserID></s:StudyUnit>'
            '</ddi:DDIInstance>',
            base_url='some.base',
            identifier='oai_rec_1'
        )).studies)
        self.assertEqual(len(studies), 1)
        study = studies[0]
        self.assertEqual(len(study.identifiers), 0)

    def test_primary_data_access(self):
        """Make sure
        ddi:DDIInstance/s:StudyUnit/a:Archive/a:ArchiveSpecific/a:Item/a:Access/r:Description/r:Content
        is read into data_access and all other lookups are skipped.
        Issue at github:
        https://github.com/cessda/cessda.cdc.aggregator.shared-library/issues/53
        """
        studies = list(self.ParserClass.from_string(_valid_root(
            metadata=self._ddi_instance_root +
            '<s:StudyUnit><a:Archive><a:ArchiveSpecific>'
            '<a:Item><a:Access><r:Description>'
            '<r:Content>Primary</r:Content>'
            '</r:Description></a:Access></a:Item>'
            '<a:DefaultAccess><a:Restrictions>'
            '<r:Content>Secondary</r:Content>'
            '</a:Restrictions></a:DefaultAccess>'
            '</a:ArchiveSpecific></a:Archive></s:StudyUnit>'
            '</ddi:DDIInstance>',
            base_url='some.base',
            identifier='some_id')).studies)
        self.assertEqual(len(studies), 1)
        study = studies[0]
        self.assertEqual(len(study.data_access), 1)
        self.assertEqual(study.data_access[0].get_value(), 'Primary')

    def test_data_access_fallback(self):
        """Make sure if
        ddi:DDIInstance/s:StudyUnit/a:Archive/a:ArchiveSpecific/a:Item/a:Access/r:Description/r:Content
        is not found, we fallback to old source XPATHs
        """
        studies = list(self.ParserClass.from_string(_valid_root(
            metadata=self._ddi_instance_root +
            '<s:StudyUnit><a:Archive><a:ArchiveSpecific>'
            '<a:Item><a:Access><r:Description>'
            '</r:Description></a:Access></a:Item>'
            '<a:DefaultAccess><a:Restrictions>'
            '<r:Content>Secondary</r:Content>'
            '</a:Restrictions></a:DefaultAccess>'
            '</a:ArchiveSpecific></a:Archive></s:StudyUnit>'
            '</ddi:DDIInstance>',
            base_url='some.base',
            identifier='some_id')).studies)
        self.assertEqual(len(studies), 1)
        study = studies[0]
        self.assertEqual(len(study.data_access), 1)
        self.assertEqual(study.data_access[0].get_value(), 'Secondary')

    def test_data_access_descriptions_primary(self):
        """Make sure
        ddi:DDIInstance/s:StudyUnit/a:Archive/a:ArchiveSpecific/a:Item/a:Access/a:TypeOfAccess
        is read into data_access_descriptions and all other source
        xpaths are skipped.

        Issue at github: https://github.com/cessda/cessda.cdc.aggregator.shared-library/issues/54
        """
        studies = list(self.ParserClass.from_string(_valid_root(
            metadata=self._ddi_instance_root +
            '<s:StudyUnit><a:Archive><a:ArchiveSpecific><a:Item><a:Access>'
            '<a:TypeOfAccess controlledVocabularyName="elem_vers">primary</a:TypeOfAccess>'
            '</a:Access></a:Item><a:DefaultAccess><a:AccessConditions>'
            '<r:Content>secondary</r:Content>'
            '</a:AccessConditions></a:DefaultAccess></a:ArchiveSpecific></a:Archive>'
            '</s:StudyUnit></ddi:DDIInstance>',
            base_url='some.base',
            identifier='someid')).studies)
        self.assertEqual(len(studies), 1)
        study = studies[0]
        self.assertEqual(len(study.data_access_descriptions), 1)
        self.assertEqual(study.data_access_descriptions[0].get_value(), 'primary')
        self.assertEqual(study.data_access_descriptions[0].attr_element_version.get_value(), 'elem_vers')

    def test_data_access_descriptions_fallback(self):
        """If
        ddi:DDIInstance/s:StudyUnit/a:Archive/a:ArchiveSpecific/a:Item/a:Access/a:TypeOfAccess
        is not found we fallback to old source.

        Issue at github: https://github.com/cessda/cessda.cdc.aggregator.shared-library/issues/54
        """
        studies = list(self.ParserClass.from_string(_valid_root(
            metadata=self._ddi_instance_root +
            '<s:StudyUnit><a:Archive><a:ArchiveSpecific><a:Item><a:Access>'
            '</a:Access></a:Item><a:DefaultAccess><a:AccessConditions>'
            '<r:Content>secondary</r:Content>'
            '</a:AccessConditions></a:DefaultAccess></a:ArchiveSpecific></a:Archive>'
            '</s:StudyUnit></ddi:DDIInstance>',
            base_url='some.base',
            identifier='someid')).studies)
        self.assertEqual(len(studies), 1)
        study = studies[0]
        self.assertEqual(len(study.data_access_descriptions), 1)
        self.assertEqual(study.data_access_descriptions[0].get_value(), 'secondary')
        self.assertEqual(study.data_access_descriptions[0].attr_element_version.get_value(), None)
