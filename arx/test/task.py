import pkg_resources

import yaml

from ..task import Task


def test_basic():
    text = pkg_resources.resource_string(__package__, 'basic.yaml')
    data = yaml.load(text)
    task = Task(data)
    assert len(task.code) == 2
    assert len(task.data) == 2
    assert len(task.to_primitive()) > 0


def test_expanded():
    text = pkg_resources.resource_string(__package__, 'expanded.yaml')
    data = yaml.load(text)
    task = Task(data)
    assert len(task.code) == 2
    assert len(task.data) == 2
    assert len(task.to_primitive()) > 0
