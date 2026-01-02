import argparse
import sys

from pyramid.paster import bootstrap, get_appsettings, setup_logging
from sqlalchemy.exc import OperationalError

from .. import models
from ..models.user import get_or_create_user_by_email
from ..models import Shop


def setup_models(dbsession, settings):
    """
    Add or update models / fixtures in the database.

    """
    # model = models.mymodel.MyModel(name='one', value=1)
    # dbsession.add(model)
    root_domain_shop = Shop(
        settings["app.root_domain"],
        "000-000-0000",
        "none",
        "Reserved shop for SaaS root domain.",
    )
    root_domain_shop.domain_name = settings["app.root_domain"]

    dbsession.add(root_domain_shop)
    dbsession.flush()

    root_domain_owner = get_or_create_user_by_email(
        dbsession, settings["app.root_domain_owner_email"]
    )

    dbsession.add(root_domain_owner)
    dbsession.flush()

    us = root_domain_shop.add_user_to_shop(root_domain_owner, role_id=0)

    dbsession.add(us)
    dbsession.flush()


def parse_args(argv):
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "config_uri",
        help="Configuration file, e.g., development.ini",
    )
    return parser.parse_args(argv[1:])


def main(argv=sys.argv):
    args = parse_args(argv)
    setup_logging(args.config_uri)
    env = bootstrap(args.config_uri)

    settings = get_appsettings(args.config_uri)
    engine = models.get_engine(settings)
    models.meta.Base.metadata.create_all(engine)

    try:
        with env["request"].tm:
            dbsession = env["request"].dbsession
            # setup_models(dbsession, settings)
    except OperationalError:
        print(
            """
Pyramid is having a problem using your SQL database.  The problem
might be caused by one of the following things:

1.  You may need to initialize your database tables with `alembic`.
    Check your README.txt for description and try to run it.

2.  Your database server may not be running.  Check that the
    database server referred to by the "sqlalchemy.url" setting in
    your "development.ini" file is running.
            """
        )
