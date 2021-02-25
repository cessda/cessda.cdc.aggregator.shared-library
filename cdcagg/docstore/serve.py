import logging
from py12flogging.log_formatter import (
    setup_app_logging,
    set_ctx_populator
)
from kuha_common import conf
from kuha_common.server import (
    serve,
    serverlog_ctx_populator
)
from cdcagg import list_collection_names
from .http_api import get_app
from . import controller


_logger = logging.getLogger(__name__)


def add_cli_args(parser):
    parser.add('-p', '--port',
               help='Port to listen to',
               default=6001, type=int, env_var='CDCADD_PORT')
    parser.add('--api-version',
               help='HTTP API version gets prepended to URLs',
               default='v0', type=str, env_var='CDCADD_API_VERSION')
    parser.add('--process-count', default=0, type=int, env_var='CDCAGG_PROCESS_COUNT',
               help='Number of forked processes. 0 forks multiple tornado server processes.')


def main():
    parser = conf.load(prog='cdcagg.docstore')
    conf.add_print_arg()
    conf.add_config_arg()
    conf.add_loglevel_arg()
    add_cli_args(parser)
    controller.add_cli_args(parser)
    settings = conf.get_conf()
    if settings.print_configuration:
        print('Print active configuration and exit\n')
        conf.print_conf()
        return 0
    set_ctx_populator(serverlog_ctx_populator)
    setup_app_logging('cdcagg.docstore', loglevel=settings.loglevel, port=settings.port)
    try:
        db = controller.db_from_settings(settings)
        app = get_app(settings.api_version,
                      list_collection_names(),
                      db=db)
    except:
        # TODO Logger
        _logger.exception('Exception in application setup')
        raise
    try:
        serve(app, settings.port, settings.process_count, on_exit=db.close)
    except KeyboardInterrupt:
        _logger.warning('Shutdown by CTRL + C', exc_info=True)
    except:
        _logger.exception('Unhandled exception in main()')
        raise
    finally:
        _logger.info('Exiting')
    return 0
