from celery import shared_task


@shared_task
def update_feature_flags(force: bool = False):
    """
    Update feature flags definitions.
    """
    from weni.feature_flags.services import FeatureFlagsService

    FeatureFlagsService().update_features(force=force)
