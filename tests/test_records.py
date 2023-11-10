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

import unittest

from cdcagg_common import records


class TestStudy(unittest.TestCase):

    def test_create_new_record_fabricates_aggregator_attrs(self):
        self.assertTrue(hasattr(records.Study._provenance, 'fabricate'))
        self.assertTrue(hasattr(records.Study._direct_base_url, 'fabricate'))
        self.assertTrue(hasattr(records.Study._aggregator_identifier, 'fabricate'))
        s = records.Study()
        self.assertFalse(hasattr(s._provenance, 'fabricate'))
        self.assertFalse(hasattr(s._direct_base_url, 'fabricate'))
        self.assertFalse(hasattr(s._aggregator_identifier, 'fabricate'))
        self.assertTrue(hasattr(records.Study._provenance, 'fabricate'))
        self.assertTrue(hasattr(records.Study._direct_base_url, 'fabricate'))
        self.assertTrue(hasattr(records.Study._aggregator_identifier, 'fabricate'))

    def test_set_direct_base_url_raises_ValueError_if_already_set(self):
        s = records.Study()
        s.set_direct_base_url('some.url')
        with self.assertRaises(ValueError):
            s.set_direct_base_url('another.url')

    def test_export_provenance_dict(self):
        s = records.Study()
        s._provenance.add_value('2000-01-01T23:00:00Z', altered=True, base_url='some_base_url',
                                identifier='some_id', datestamp='1999-01-01T00:00:00Z',
                                direct=True, metadata_namespace='some_namespace')
        s._provenance.add_value('1999-01-01T23:00:00Z', altered=True, base_url='some_base_url',
                                identifier='some_id', datestamp='1999-01-01T00:00:00Z',
                                direct=False, metadata_namespace='some_namespace')
        expecteds = {'2000-01-01T23:00:00Z': {'altered': True, 'base_url': 'some_base_url', 'identifier': 'some_id',
                                              'datestamp': '1999-01-01T00:00:00Z', 'direct': True,
                                              'metadata_namespace': 'some_namespace'},
                     '1999-01-01T23:00:00Z': {'altered': True, 'base_url': 'some_base_url', 'identifier': 'some_id',
                                              'datestamp': '1999-01-01T00:00:00Z', 'direct': False,
                                              'metadata_namespace': 'some_namespace'}}
        for prov in s.export_provenance_dict()['_provenance']:
            hd = prov.pop('harvest_date')
            self.assertIn(hd, expecteds)
            expected = expecteds.pop(hd)
            self.assertEqual(prov, expected)
        self.assertEqual(expecteds, {})

    def test_export_provenance_dict_returns_keys(self):
        s = records.Study()
        self.assertEqual(list(s.export_provenance_dict().keys()),
                         ['_provenance', '_aggregator_identifier', '_direct_base_url'])

    def test_export_direct_provenance_dict_exports_base_url(self):
        s = records.Study()
        s._direct_base_url.add_value('some.base.url')
        self.assertEqual(s.export_provenance_dict()['_direct_base_url'], 'some.base.url')

    def test_imports_existing_record_provenances(self):
        s = records.Study()
        s._provenance.add_value('2000-01-01T23:00:00Z', altered=True, base_url='some_base_url',
                                identifier='some_id', datestamp='1999-01-01T00:00:00Z',
                                direct=True, metadata_namespace='some_namespace')
        s._provenance.add_value('1999-01-01T23:00:00Z', altered=True, base_url='some_base_url',
                                identifier='some_id', datestamp='1999-01-01T00:00:00Z',
                                direct=False, metadata_namespace='some_namespace')
        s._aggregator_identifier.set_value('f75518a990fa45168baf74d7f58ae06d')
        imported = records.Study(s.export_dict(include_provenance=True,
                                               include_metadata=True,
                                               include_id=True))
        expecteds = {'2000-01-01T23:00:00Z': {'altered': True, 'base_url': 'some_base_url', 'identifier': 'some_id',
                                              'datestamp': '1999-01-01T00:00:00Z', 'direct': True,
                                              'metadata_namespace': 'some_namespace'},
                     '1999-01-01T23:00:00Z': {'altered': True, 'base_url': 'some_base_url', 'identifier': 'some_id',
                                              'datestamp': '1999-01-01T00:00:00Z', 'direct': False,
                                              'metadata_namespace': 'some_namespace'}}
        for prov in imported.export_provenance_dict()['_provenance']:
            hd = prov.pop('harvest_date')
            self.assertIn(hd, expecteds)
            expected = expecteds.pop(hd)
            self.assertEqual(prov, expected)
        self.assertEqual(expecteds, {})
        self.assertEqual(s._aggregator_identifier.get_value(), imported._aggregator_identifier.get_value())

    def test_imports_existing_record_direct_base_url(self):
        s = records.Study()
        s._direct_base_url.add_value('some.url')
        imported = records.Study(s.export_dict(include_provenance=True, include_metadata=True, include_id=True))
        self.assertEqual(imported.export_provenance_dict()['_direct_base_url'], 'some.url')
