from flask_unchained.bundles.sqlalchemy.base_model import BaseModel
from py_meta_utils import McsArgs, MetaOption
from sqlalchemy_unchained import ModelMetaOptionsFactory


class ExtendExisting(MetaOption):
    def __init__(self):
        super().__init__(name="extend_existing", default=True, inherit=False)

    def check_value(self, value, mcs_args: McsArgs):
        msg = f"{self.name} Meta option on {mcs_args.qualname} must be True or False"
        assert isinstance(value, bool), msg

    def contribute_to_class(self, mcs_args, value):
        if not value:
            return

        table_args = mcs_args.clsdict.get("__table_args__", {})
        table_args["extend_existing"] = True
        mcs_args.clsdict["__table_args__"] = table_args


class CustomModelMetaOptions(ModelMetaOptionsFactory):
    def _get_meta_options(self):
        return super()._get_meta_options() + [
            ExtendExisting(),
        ]


class Model(BaseModel):
    _meta_options_factory_class = CustomModelMetaOptions

    class Meta:
        _testing_ = "overriding the default"
        abstract = True
        extend_existing = True
        pk = "pk"
