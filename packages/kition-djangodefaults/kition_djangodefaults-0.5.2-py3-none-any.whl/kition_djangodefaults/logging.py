import logging

from django.core.exceptions import ImproperlyConfigured


def configure_logging_to_skip_exception(LOGGING, ExceptionClass, level=logging.WARNING):
    if "filters" in LOGGING and "skip_exception" in LOGGING["filters"]:
        raise ImproperlyConfigured(
            "This method assumes to be called once as a second call overrides the previous calls changes. Support "
            "checking multiple exceptions in the filter if required."
        )

    def skip_exception(record):
        if record.exc_info:
            exc_type, exc_value = record.exc_info[:2]
            if isinstance(exc_value, ExceptionClass):
                return False
        return True

    LOGGING.setdefault("filters", {}).update(
        {
            "skip_exception": {
                "()": "django.utils.log.CallbackFilter",
                "callback": skip_exception,
            }
        }
    )

    LOGGING.setdefault("loggers", {}).update(
        {
            "django.request": {
                "filters": ["skip_exception"],
                "level": logging.getLevelName(level),
            }
        }
    )
