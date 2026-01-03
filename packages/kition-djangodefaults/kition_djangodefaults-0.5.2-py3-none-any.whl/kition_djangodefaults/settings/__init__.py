def initialize_default_settings(settings_module_name: str):
    """
    Initialize the Kition default settings within your applications settings module. The Django default settings are
    already applied. Any settings defined in your settings module take precedence.

    Call it like `initialize_default_settings(__name__)` within the settings module.

    :param settings_module_name: `__name__` of the applications settings module
    """
    import sys
    from django.conf import Settings

    settings_module = sys.modules[settings_module_name]
    default_settings = Settings("kition_djangodefaults.settings.default")

    for key in default_settings.__dict__.keys():
        if key.isupper():
            setattr(settings_module, key, default_settings.__dict__[key])
