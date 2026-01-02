def includeme(config):
    JINJA2_EXTENSION = ".j2"
    config.include("pyramid_jinja2")
    config.add_jinja2_renderer(JINJA2_EXTENSION)
    config.add_jinja2_search_path("templates", name=JINJA2_EXTENSION)
