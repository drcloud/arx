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
        for cls, col in [(Code, self.code), (Data, self.data)]:
            if isinstance(arg, cls):
                col += [arg]
                return self
        raise TypeError('Bundles can only append Code or Data instances.')

    def __isub__(self, arg):
        for cls, col in [(Code, self.code), (Data, self.data)]:
            if isinstance(arg, cls):
                for idx in [i for i, el in enumerate(col) if arg == el]:
                    del col[idx]
                return self
        raise TypeError('Bundles can only remove Code or Data instances.')
