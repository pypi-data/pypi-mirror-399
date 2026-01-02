from pyramid.config import Configurator
from pyramid.session import SignedCookieSessionFactory
from pyramid.session import JSONSerializer

import re


class SpamBlockerMiddleware:
    """
    Middleware to block spammy requests based on query string patterns.
    """

    def __init__(self, app):
        self.app = app

    def __call__(self, environ, start_response):
        # Extract the query string
        query_string = environ.get("QUERY_STRING", "")

        # Define regex patterns
        unescaped_next_count = len(re.findall(r"(?i)\bnext=", query_string))
        escaped_next_count = len(
            re.findall(r"(?i)\bnext%25|next%3D|next%253D|next%2525", query_string)
        )

        # Check if the request is spammy
        if unescaped_next_count + escaped_next_count > 1:
            # Respond with 401 Unauthorized
            print("next= query spam detected.")
            status = "401 Unauthorized"
            headers = [("Content-Type", "text/plain")]
            start_response(status, headers)
            return [b"Request appears malformed or spammy.\n"]

        # Forward the request to the next application/middleware
        return self.app(environ, start_response)

    def __getattr__(self, name):
        """
        Delegate attribute access to the wrapped Pyramid app.
        This ensures that attributes like 'registry' are accessible.
        """
        return getattr(self.app, name)


def get_int_or_bool_or_none_or_str(value):
    """
    Given a string value pulled from a configuration file,
    this function attempts to return the value with the proper type.
    """
    # Handle non-string values
    if not isinstance(value, str):
        return value

    # Handle string values
    try:
        return int(value)
    except ValueError:
        value_lower = value.lower()
        if value_lower in {"yes", "y", "true", "t", "1"}:
            return True
        elif value_lower in {"no", "n", "false", "f", "0"}:
            return False
        elif value_lower in {"none", "null"}:
            return None
        return str(value)


def expand_env_vars(value):
    """Expand environment variables including ${VAR:-default} syntax."""
    if not isinstance(value, str):
        return value

    import os
    import re

    # First try os.path.expandvars for simple cases
    value = os.path.expandvars(value)

    # Then handle ${VAR:-default} syntax
    # Use a non-greedy match to stop at the first closing brace
    pattern = r"\$\{([^:}]*)(?::-([^}]*?))?\}"

    def replacer(match):
        var_name = match.group(1)
        # Handle empty variable name case ${:-default}
        if not var_name:
            return match.group(2) if match.group(2) is not None else match.group(0)
        default_value = match.group(2) if match.group(2) is not None else ""
        return os.environ.get(var_name, default_value)

    return re.sub(pattern, replacer, value)


def get_children_settings(settings, parent_key):
    """
    Accept a settings dict and parent key, return dict of children

    For example:

      auth_tkt.hashalg = md5

    Results to:

      {'auth_tkt.hashalg': 'md5'}

    This function returns the following:

      >>> get_children_settings({'auth_tkt.hashalg': 'md5'}, 'auth_tkt')
      {'hashalg': 'md5'}

    """
    # the +1 is the . between parent and child settings.
    parent_len = len(parent_key) + 1
    children = {}
    for key, value in settings.items():
        if parent_key in key:
            # Expand environment variables with support for defaults
            expanded_value = expand_env_vars(value)
            children[key[parent_len:]] = get_int_or_bool_or_none_or_str(expanded_value)
    return children


def main(global_config, **settings):
    """This function returns a Pyramid WSGI application."""

    # Expand environment variables in all settings using our custom function
    for key, value in list(settings.items()):
        if isinstance(value, str):
            settings[key] = expand_env_vars(value)

    # Setup session factory signed cookies prevent tampering, not encrypted.
    session_settings = get_children_settings(settings, "session")

    # Setup session serializer.
    session_settings["serializer"] = JSONSerializer()

    session_factory = SignedCookieSessionFactory(**session_settings)

    with Configurator(settings=settings, session_factory=session_factory) as config:
        # all of the models for persisting data into our database.
        config.include(".models")
        # all of the web application routes.
        config.include(".routes")
        # all of the data we attach to each inbound request.
        config.include(".request_methods")
        # enable jinja2 templating engine.
        config.include(".config_jinja2")
        # scan each of these includes for additional configuration.
        config.scan()

        # generate app.
        app = config.make_wsgi_app()

        # Wrap the Pyramid app with SpamBlockerMiddleware.
        app = SpamBlockerMiddleware(app)

    return app
