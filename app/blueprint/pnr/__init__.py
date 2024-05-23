from flask import Blueprint

pr = Blueprint('pr', __name__)

from . import routes