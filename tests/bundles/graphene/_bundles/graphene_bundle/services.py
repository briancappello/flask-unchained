from flask_unchained.bundles.sqlalchemy import ModelManager

from . import models


class ParentManager(ModelManager):
    class Meta:
        model = models.Parent


class ChildManager(ModelManager):
    class Meta:
        model = models.Child
