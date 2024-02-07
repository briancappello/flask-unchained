from wtforms.fields import *

try:
    from wtforms.fields.html5 import *
except ImportError:
    pass
from flask_wtf.file import FileField
