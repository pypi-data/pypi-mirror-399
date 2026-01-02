from pyramid.view import view_config

from . import user_required


@view_config(route_name="actions_view", renderer="actions_view.j2")
@user_required()
def view_actions(request):
    return {}


@view_config(route_name="actions_new", renderer="actions_new.j2")
@user_required()
def new_actions(request):
    return {}
