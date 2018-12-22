#!/usr/bin/env python3

import os

from flask import Flask
from flask_sqlalchemy import SQLAlchemy

# --------------------------------------------------------------------------------

app = Flask(__name__)

if 'CELLAR_DATA' in os.environ:
	app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['CELLAR_DATA']
else:
	app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.getcwd() + '/data/cellar.db'

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# --------------------------------------------------------------------------------

from .data_model import *
