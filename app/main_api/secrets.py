# Flask settings
FLASK_SECRET_KEY = 'paPTvnNME5NBHHuIOlFqG6zS77vHadbo'

# SQLAlchemy settings
#SQLALCHEMY_DATABASE_URI = 'postgresql://hotmaps:Dractwatha9@172.17.0.12:5432/toolboxdb'
#SQLALCHEMY_DATABASE_URI = 'postgresql://hotmaps:Dractwatha9@hotmaps.hevs.ch:32767/toolboxdb'
SQLALCHEMY_DATABASE_URI_DEVELOPMENT = 'postgresql://hotmaps:Dractwatha9@hotmapsdev.hevs.ch:32768/toolboxdb'
SQLALCHEMY_DATABASE_URI_PRODUCTION = 'postgresql://hotmaps:Dractwatha9@hotmaps.hevs.ch:32768/toolboxdb'
#SQLALCHEMY_DATABASE_URI_PRODUCTION = 'postgresql://hotmaps:Dractwatha9@172.17.0.5:5432/toolboxdb'
#SQLALCHEMY_DATABASE_URI_DEVELOPMENT = 'postgresql://hotmaps:Dractwatha9@172.17.0.4:5432/toolboxdb'