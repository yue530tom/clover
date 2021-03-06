
from flask import Flask
from werkzeug.utils import import_string

import config
from clover.urls import map_urls

blueprints = [
    'clover.testsuite:testsuite',
    'clover.interface:interface',
    'clover.environment:environment',
]


def create_app():
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(config)

    app.app_context().push()
    map_urls(app)

    for bp_name in blueprints:
        bp = import_string(bp_name)
        app.register_blueprint(bp)

    return app


app = create_app()
