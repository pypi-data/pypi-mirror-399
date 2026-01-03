import structlog


def configure():
    structlog.configure(
        processors=[
            structlog.stdlib.add_log_level,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.processors.dict_tracebacks,
            structlog.processors.CallsiteParameterAdder(
                [structlog.processors.CallsiteParameter.FUNC_NAME,
                 structlog.processors.CallsiteParameter.PROCESS_NAME
                 ],
            ),
            structlog.processors.JSONRenderer(indent=2, sort_keys=False),
        ],
        context_class=dict,
        cache_logger_on_first_use=True,
    )


class StructuredLogger:
    def __init__(self, name, app_info):
        configure()
        self.log = structlog.get_logger(name)
        self.log = self.log.bind(**app_info)

