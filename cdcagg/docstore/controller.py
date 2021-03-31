from kuha_document_store.database import (
    DocumentStoreDatabase,
    mongodburi
)
from kuha_document_store import validation
from cdcagg import (
    iter_collections,
    record_by_collection_name
)
from cdcagg.records import (
    Study,
    RecordBase
)


class CDCAggDatabase(DocumentStoreDatabase):

    def _get_record_by_collection(self, collection):
        return record_by_collection_name(collection.name)


def db_from_settings(settings):
    metadata_schema_items = {
        **validation.default_schema_item(RecordBase._metadata.attr_created.name),
        **validation.default_schema_item(RecordBase._metadata.attr_updated.name),
        **validation.default_schema_item(RecordBase._metadata.attr_deleted.name, nullable=True),
        **validation.default_schema_item(RecordBase._metadata.attr_cmm_type.name),
        # TODO ENUM schema item
        **validation.default_schema_item(RecordBase._metadata.attr_status.name),
        # TODO float schema item
        **validation.default_schema_item(RecordBase._metadata.attr_schema_version.name)
    }
    provenance_schema_items = {
        **validation.default_schema_item(RecordBase._provenance.attr_base_url.name),
        **validation.default_schema_item(RecordBase._provenance.attr_identifier.name),
        **validation.default_schema_item(RecordBase._provenance.attr_datestamp.name),
        **validation.default_schema_item(RecordBase._provenance.attr_metadata_namespace.name),
        **validation.default_schema_item(RecordBase._provenance.sub_name.name),
        **validation.bool_schema_item(RecordBase._provenance.attr_altered.name),
        **validation.bool_schema_item(RecordBase._provenance.attr_direct.name)
    }
    base_schema = {
        **validation.identifier_schema_item(RecordBase._aggregator_identifier.path),
        **validation.dict_schema_item(RecordBase._metadata.path, metadata_schema_items),
        **validation.container_schema_item(RecordBase._provenance.path, provenance_schema_items)}
    validation.add_schema(Study.collection,
                          validation.RecordValidationSchema(
                              Study,
                              base_schema,
                              validation.identifier_schema_item(Study.study_number.path),
                              validation.uniquelist_schema_item(Study.persistent_identifiers.path),
                              validation.bool_schema_item(Study.universes.attr_included.path)
                          ))
    reader_uri = mongodburi(*settings.replica, database=settings.database_name,
                            credentials=(settings.database_user_reader,
                                         settings.database_pass_reader))
    editor_uri = mongodburi(*settings.replica, database=settings.database_name,
                            credentials=(settings.database_user_editor,
                                         settings.database_pass_editor))
    return CDCAggDatabase(collections=list(iter_collections()),
                          name=settings.database_name,
                          reader_uri=reader_uri, editor_uri=editor_uri)


def add_cli_args(parser):
    parser.add('--replica', 
               help='MongoDB replica replica host + port. Repeat for multiple replicas. For example: localhost:27017',
               env_var='DBREPLICAS',
               action='append',
               required=True,
               type=str)
    parser.add('--replicaset',
               help='MongoDB replica set name',
               env_var='DBREPLICASET',
               default='rs_cdcagg',
               type=str)
    parser.add('--database-name',
               help='Database name',
               default='cdcagg',
               env_var='DBNAME',
               type=str)
    parser.add('--database-user-reader',
               help='Username for reading from the database',
               default='reader',
               env_var='DBUSER_READER',
               type=str)
    parser.add('--database-pass-reader',
               help='Password for database-user-reader',
               default='reader',
               env_var='DBPASS_READER',
               type=str)
    parser.add('--database-user-editor',
               help='Username for editing the database',
               default='editor',
               env_var='DBUSER_EDITOR',
               type=str)
    parser.add('--database-pass-editor',
               help='Password for database-user-editor',
               default='editor',
               env_var='DBPASS_EDITOR',
               type=str)

