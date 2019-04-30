#! /usr/bin/env python3

from flask import Flask
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand

from app import db


'''
To upgrade database, run following commands:
python3 manage.py db init  (run only once)
python3 manage.py db migrate 
python3 manage.py db upgrade 
'''

flaskapp = Flask(__name__)

# Configurations
flaskapp.config.from_pyfile('app/config.py')

# import database and models

migrate = Migrate(flaskapp, db)
manager = Manager(flaskapp)
manager.add_command('db', MigrateCommand)

if __name__ == '__main__':
    manager.run()


