from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


def reset_database():
    from main_api.models import nuts, population_density  # noqa
    db.drop_all()
    db.create_all()
