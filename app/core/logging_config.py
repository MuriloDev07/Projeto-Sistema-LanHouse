import logging
import sys

def configure_logging(app):
    """
    Configura o logger padrão de aplicação Flask para emitir logs formatados no stdout.
    """
    app.logger.handlers.clear()
    log_format = logging.Formatter(
        '[%(asctime)s] [%(levelname)s] [%(name)s em %(filename)s:%(lineno)d] %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setFormatter(log_format)
    stream_handler.setLevel(logging.INFO)

    app.logger.addHandler(stream_handler)
    app.logger.setLevel(logging.INFO)

    logging.getLogger('werkzeug').setLevel(logging.WARNING)

    app.logger.info("Módulo de Logging inicializado com sucesso.")