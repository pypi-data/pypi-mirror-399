from django.apps import AppConfig


class WeniFeatureFlagsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "weni.feature_flags"
    label = "weni_feature_flags"
