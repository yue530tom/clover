"""
# url mapping for views
# /api/version/module/function
"""
from clover.environment.views import EnvironmentView as Environment
from clover.interface.views import InterfaceView as Interface
from clover.testsuite.views import TestSuiteView as TestSuite


def map_urls(app):
    # 配置管理相关路由与视图
    environment = Environment.as_view("environment")
    app.add_url_rule(
        "/api/v1/environment/create",
        view_func=environment,
        methods=['POST'],
        strict_slashes=False,
    )
    app.add_url_rule(
        "/api/v1/environment/delete",
        view_func=environment,
        methods=['POST'],
        strict_slashes=False,
    )
    app.add_url_rule(
        "/api/v1/environment/update",
        view_func=environment,
        methods=['POST'],
        strict_slashes=False,
    )
    app.add_url_rule(
        "/api/v1/environment/search",
        view_func=environment,
        methods=['GET'],
        strict_slashes=False,
    )
    app.add_url_rule(
        "/api/v1/environment/aggregate",
        view_func=environment,
        methods=['POST'],
        strict_slashes=False,
    )
    app.add_url_rule(
        "/api/v1/environment/debug",
        view_func=environment,
        methods=['POST'],
        strict_slashes=False,
    )
    app.add_url_rule(
        "/api/v1/environment/save",
        view_func=environment,
        methods=['POST'],
        strict_slashes=False,
    )

    # 接口测试相关路由与视图
    interface = Interface.as_view("interface")
    app.add_url_rule(
        "/api/v1/interface/save",
        view_func=interface,
        methods=['POST'],
        strict_slashes=False,
    )
    app.add_url_rule(
        "/api/v1/interface/debug",
        view_func=interface,
        methods=['POST'],
        strict_slashes=False,
    )
    app.add_url_rule(
        "/api/v1/interface/trigger",
        view_func=interface,
        methods=['GET', 'POST'],
        strict_slashes=False,
    )
    app.add_url_rule(
        "/api/v1/interface/delete",
        view_func=interface,
        methods=['POST'],
        strict_slashes=False,
    )
    app.add_url_rule(
        "/api/v1/interface/search",
        view_func=interface,
        methods=['GET', 'POST'],
        strict_slashes=False,
    )

    # 测试套件相关路由与视图
    testsuite = TestSuite.as_view("testsuite")
    app.add_url_rule(
        "/api/v1/testsuite/create",
        view_func=testsuite,
        methods=['POST'],
        strict_slashes=False,
    )
    app.add_url_rule(
        "/api/v1/testsuite/delete",
        view_func=testsuite,
        methods=['POST'],
        strict_slashes=False,
    )
    app.add_url_rule(
        "/api/v1/testsuite/update",
        view_func=testsuite,
        methods=['POST'],
        strict_slashes=False,
    )
    app.add_url_rule(
        "/api/v1/testsuite/search",
        view_func=testsuite,
        methods=['GET', 'POST'],
        strict_slashes=False,
    )
