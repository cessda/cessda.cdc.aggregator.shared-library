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

"""There is no good reason to test contants defined in mdb_const.py.
However, since the SonarQube coverage complains about missing lines
in mdb_const.py, we'll import the package here to make sure no exceptions are
raised on import"""

from unittest import TestCase


class TestMDBConst(TestCase):

    def test_no_exception_raised_on_import(self):
        try:
            from cdcagg_common import mdb_const
        except Exception as exc:
            raise AssertionError("Exception raised on import") from exc
