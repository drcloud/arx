from schematics.types import StringType
from schematics.types.compound import DictType, ListType, ModelType
from schematics.models import Model


class Source(Model):
    formerly = ListType(StringType())

    def convert(self, raw_data, **kwargs):
        raise NotImplementedError()


class Command(Model):
    source = ModelType(Source)
    cmd = ListType(StringType())

    def convert(self, raw_data, **kwargs):
        raise NotImplementedError()


class Code(Model):
    cmd = ModelType(Command)
    args = ListType(StringType())
    cwd = StringType()
    env = DictType()
    label = StringType()

    def convert(self, raw_data, **kwargs):
        raise NotImplementedError()


class Data(Model):
    source = ModelType(Source, required=True)
    target = StringType()


class Task(Model):
    code = ListType(ModelType(Code))
    data = ListType(ModelType(Data))
    cwd = StringType()
    env = DictType()
    label = StringType()
