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

from unittest import TestCase
import cdcagg_common


class TestCdcAggPackage(TestCase):

    def test_list_collection_names_return_collection_names(self):
        self.assertEqual(cdcagg_common.list_collection_names(), ['studies'])

    def test_list_records_lists_all_records(self):
        self.assertEqual(cdcagg_common.list_records(), [cdcagg_common.Study])

    def test_record_by_collection_returns_None(self):
        self.assertEqual(cdcagg_common.record_by_collection_name('nonexistent'), None)

    def test_record_by_collection_returns_study_class(self):
        self.assertEqual(cdcagg_common.record_by_collection_name('studies'), cdcagg_common.Study)
