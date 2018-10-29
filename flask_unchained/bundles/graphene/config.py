from flask_unchained import BundleConfig


class Config(BundleConfig):
    GRAPHENE_URL = '/graphql'
    """
    The URL where graphene should be served from. Set to ``None`` to disable.
    """

    GRAPHENE_BATCH_URL = None
    """
    The URL where graphene should be served from in batch mode. Set to ``None``
    to disable.
    """

    GRAPHENE_ENABLE_GRAPHIQL = False
    """
    Whether or not to enable GraphIQL.
    """

    GRAPHENE_PRETTY_JSON = False
    """
    Whether or not to pretty print the returned JSON.
    """


class DevConfig(Config):
    GRAPHENE_ENABLE_GRAPHIQL = True
    """
    Whether or not to enable GraphIQL.
    """

    GRAPHENE_PRETTY_JSON = True
    """
    Whether or not to pretty print the returned JSON.    
    """
