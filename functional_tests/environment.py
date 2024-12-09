def before_all(context):
    # Set up any global configurations
    context.config.setup_logging()


def after_scenario(context, scenario):
    # Clean up after each scenario
    if hasattr(context, 'csv_reader'):
        del context.csv_reader
    if hasattr(context, 'api_client'):
        del context.api_client


def before_feature(context, feature):
    # Set up feature-specific configurations
    pass


def after_feature(context, feature):
    # Clean up after feature
    pass