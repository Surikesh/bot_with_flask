from flask import Flask
from settings import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate, MigrateCommand
from flask_script import Manager
app = Flask(__name__)
app.config.from_object(Config)

db = SQLAlchemy(app)
db.create_all()
migrate = Migrate(app, db)
manager = Manager(app)

manager.add_command('db', MigrateCommand)

migrate.init_app(app, db)

from .models import Users
