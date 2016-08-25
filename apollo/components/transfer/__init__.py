from flask import Blueprint
blueprint = Blueprint('transfer', __name__)

from .subscribers import (transfer_subscriber)
