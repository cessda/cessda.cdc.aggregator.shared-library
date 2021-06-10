import unittest
from unittest import mock

from cdcagg_common import records


class TestStudy(unittest.TestCase):

    def test_creates_new_record(self):
        records.Study()

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
