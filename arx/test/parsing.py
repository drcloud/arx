import pkg_resources

import yaml

from .. import arx


def test_basic():
    text = pkg_resources.resource_string(__package__, 'basic.yaml')
    data = yaml.load(text)
    bundle = arx.Bundle(data)
    assert len(bundle.code) == 2
    assert len(bundle.data) == 2
    assert len(bundle.to_primitive()) > 0


def test_expanded():
    text = pkg_resources.resource_string(__package__, 'expanded.yaml')
    data = yaml.load(text)
    bundle = arx.Bundle(data)
    assert len(bundle.code) == 2
    assert len(bundle.data) == 2
    assert len(bundle.to_primitive()) > 0
