from kuha_document_store.database import (
    DocumentStoreDatabase,
    mongodburi,
    validate  # TODO proper validate
)
from cdcagg import (
    iter_collections,
    record_by_collection_name
)


class CDCAggDatabase(DocumentStoreDatabase):

    def _get_record_by_collection(self, collection):
        return record_by_collection_name(collection.name)


def db_from_settings(settings):
    collections = list(iter_collections())
    reader_uri = mongodburi(*settings.replica, database=settings.database_name,
                            credentials=(settings.database_user_reader,
                                         settings.database_pass_reader))
    editor_uri = mongodburi(*settings.replica, database=settings.database_name,
                            credentials=(settings.database_user_editor,
                                         settings.database_pass_editor))
    return CDCAggDatabase(collections=collections, name=settings.database_name,
                          reader_uri=reader_uri, editor_uri=editor_uri)


def add_cli_args(parser):
    parser.add('--replica', 
               help='MongoDB replica replica host + port. Repeat for multiple replicas. For example: localhost:27017',
               env_var='CDCAGG_DBREPLICAS',
               action='append',
               required=True,
               type=str)
    parser.add('--replicaset',
               help='MongoDB replica set name',
               env_var='CDCAGG_DBREPLICASET',
               default='rs_cdcagg',
               type=str)
    parser.add('--database-name',
               help='Database name',
               default='cdcagg',
               env_var='CDCAGG_DBNAME',
               type=str)
    parser.add('--database-user-reader',
               help='Username for reading from the database',
               default='reader',
               env_var='CDCAGG_DBUSER_READER',
               type=str)
    parser.add('--database-pass-reader',
               help='Password for database-user-reader',
               default='reader',
               env_var='CDCAGG_DBPASS_READER',
               type=str)
    parser.add('--database-user-editor',
               help='Username for editing the database',
               default='editor',
               env_var='CDCAGG_DBUSER_EDITOR',
               type=str)
    parser.add('--database-pass-editor',
               help='Password for database-user-editor',
               default='editor',
               env_var='CDCAGG_DBPASS_EDITOR',
               type=str)

