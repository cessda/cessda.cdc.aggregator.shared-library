from unittest import TestCase
from cdcagg import list_collection_names


class TestCdcAggPackage(TestCase):

    def test_list_collection_names_return_collection_names(self):
        self.assertEqual(list_collection_names(), ['studies'])
