import pytest

#! if mail:
from flask_unchained.bundles.mail.pytest import *
#! endif
#! if security or sqlalchemy:
from flask_unchained.bundles.sqlalchemy.pytest import *
#! endif
#! if security:
from flask_unchained.bundles.security.pytest import *
#! endif
