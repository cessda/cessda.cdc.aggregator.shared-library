import sys
from kuha_common.query import (
    QueryController,
    FilterKeyConstants
)
from kuha_common import conf
import kuha_client
from cdcagg import Study
from cdcagg.mappings import DDI25RecordParser


class StudyMethods(kuha_client.CollectionMethods):

    collection = Study.get_collection()

    async def query_record(self, record):
        return await QueryController().query_single(Study, _filter={
            FilterKeyConstants.and_: [
                {Study._provenance.attr_direct: True},
                {Study._provenance.attr_identifier: record._provenance[-1].attr_identifier.get_value()},
                {Study._provenance.attr_base_url: record._provenance[-1].attr_base_url.get_value()}]})

    async def query_distinct_ids(self):
        ids = await QueryController().query_distinct(Study, fieldname=Study._id)
        return set(ids[Study._id.path])

    async def remove_record_by_id(self, _id):
        return await kuha_client.send_delete_record_request(Study.get_collection(),
                                                            record_id=_id)

    async def update_record(self, new, old):
        new_dict = new.export_dict(include_provenance=False, include_metadata=False, include_id=False)
        old_dict = old.export_dict(include_provenance=False, include_metadata=False, include_id=False)
        if new_dict == old_dict:
            # Records match. No need to update.
            return False
        new_dict.update(new.export_provenance_dict())
        return await kuha_client.send_update_record_request(new.get_collection(),
                                                            new_dict, old.get_id())


def cli():
    parser = conf.load(prog='cdcagg.client.sync', package='cdcagg', env_var_prefix='CDCAGG_')
    conf.add_print_arg()
    conf.add_config_arg()
    parser.add('--document-store-url', type=str)
    parser.add('--no-remove', action='store_true')
    parser.add('--file-cache', type=str)
    parser.add('paths', nargs='+')
    settings = conf.get_conf()
    remove_absent = settings.no_remove is False
    parsers = [DDI25RecordParser]
    collections_methods = [StudyMethods]
    if settings.file_cache:
        with kuha_client.open_file_logging_cache(settings.file_cache) as cache:
            proc = kuha_client.BatchProcessor(parsers, collections_methods, cache)
            proc.upsert_run(settings.paths, remove_absent=remove_absent)
        return 0
    proc = kuha_client.BatchProcessor(parsers, collections_methods)
    proc.upsert_run(settings.paths, remove_absent=remove_absent)


if __name__ == '__main__':
    sys.exit(cli())
