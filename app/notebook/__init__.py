from flask import Blueprint

notebook = Blueprint('notebook', __name__)

from . import views
