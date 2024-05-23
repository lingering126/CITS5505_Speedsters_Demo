from flask import Blueprint

notifications_bp = Blueprint('notifications', __name__)

from . import routes  # Import routes to register them with the Blueprint