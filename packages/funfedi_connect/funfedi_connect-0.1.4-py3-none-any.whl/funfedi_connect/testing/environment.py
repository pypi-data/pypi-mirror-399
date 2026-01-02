import logging
import os

from bovine.testing.features import (
    before_all,  # noqa: F401
    before_scenario as bovine_before_scenario,
    after_scenario,  # noqa: F401
)  # noqa: F401

from funfedi_connect.applications import application_for_name
from funfedi_connect.types.feature import to_features

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def get_app_name():
    app_name = os.environ.get("FEDI_APP")
    if app_name is None:
        raise Exception("An application needs to be provided in FEDI_APP")
    return app_name


def before_feature(context, feature):
    app_name = get_app_name()
    feature.name = f"{app_name}: {feature.name}"
    context.fediverse_application = application_for_name(app_name)


def before_scenario(context, scenario):
    features = to_features(scenario.tags)
    app_features = context.fediverse_application.features

    for feature in features:
        if feature not in app_features:
            context.abort()

    if f"fix-https:{get_app_name()}" in scenario.tags:
        context.fix_https = True
    else:
        context.fix_https = False

    bovine_before_scenario(context, scenario)
