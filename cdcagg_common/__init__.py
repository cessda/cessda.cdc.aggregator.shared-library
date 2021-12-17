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
"""This package contains common code shared among all
CDC Aggregator components."""

from .records import Study


def list_records():
    """List all record classes.

    :returns: List of record classes
    :rtype: list
    """
    return [Study]


def list_collection_names():
    """List all collection names

    :returns: List of all collection names.
    :rtype: list
    """
    return [Study.get_collection()]


def record_by_collection_name(collname):
    """Get record class by collection name

    :param str collname: Collection name for lookup.
    :returns: Record class matching collname or None if no match found.
    :rtype: None or :class:`cdcagg_common.records.Study`
    """
    for rec in list_records():
        if rec.get_collection() == collname:
            return rec
    return None
