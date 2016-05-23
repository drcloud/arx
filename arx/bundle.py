from schematics.exceptions import ValidationError
from schematics.types import StringType
from schematics.types.compound import DictType, ListType, ModelType

from .inner.schematics import Model, SourceType


class Ctx(Model):
    label = StringType()
    cwd = StringType()
    env = DictType(StringType)


class Code(Ctx):
    source = SourceType()
    cmd = StringType()
    args = ListType(StringType, default=[])

    def validate_cmd_and_source(self):
        if bool(self.source) == bool(self.cmd):
            raise ValidationError('One of either Code.source or Code.cmd '
                                  'must be set -- but not both.')


class Data(Ctx):
    source = SourceType(required=True)
    target = StringType()


class Bundle(Ctx):
    code = ListType(ModelType(Code))
    data = ListType(ModelType(Data))

    def __iadd__(self, arg):
        if isinstance(arg, Code):
            self.code += [arg]
            return self
        if isinstance(arg, Data):
            self.data += [arg]
            return self
        raise TypeError('Bundles can only append Code or Data instances.')
