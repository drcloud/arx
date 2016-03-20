import pytest

from ...decorators import InvalidScheme
from ..http import HTTP, HTTPJar, HTTPTar, Invalid


def test_http():
    src = HTTP('http://aol.com/robots.txt')
    assert src.authority == 'aol.com'
    assert src.path == '/robots.txt'
    assert src.fragment is None

    with pytest.raises(Invalid):
        HTTP('https://github.com/github/gitignore#readme')

    with pytest.raises(InvalidScheme):
        src = HTTP('s3://bucket/key')

    with pytest.raises(InvalidScheme):
        src = HTTP('tar+https://aol.com/aol.tgz')

    with pytest.raises(InvalidScheme):
        src = HTTP('jar+https://github.com/github.jar')


def test_tar():
    src = HTTPTar('tar+https://github.com/github.tar#README.md')
    assert src.scheme == 'tar+https'
    assert src.authority == 'github.com'
    assert src.path == '/github.tar'
    assert src.fragment == 'README.md'

    src = HTTPTar('tar+http://aol.com/aol.tgz')
    assert src.scheme == 'tar+http'
    assert src.authority == 'aol.com'
    assert src.path == '/aol.tgz'
    assert src.fragment is None

    with pytest.raises(InvalidScheme):
        src = HTTPTar('tar+s3://bucket/key')

    with pytest.raises(InvalidScheme):
        src = HTTPTar('https://aol.com/aol.tgz')


def test_jar():
    src = HTTPJar('jar+http://aol.com/aol.jar')
    assert src.scheme == 'jar+http'
    assert src.authority == 'aol.com'
    assert src.path == '/aol.jar'
    assert src.fragment is None

    with pytest.raises(Invalid):
        HTTPJar('jar+https://github.com/github.war#web.xml')

    with pytest.raises(InvalidScheme):
        src = HTTPJar('jar+s3://bucket/key')

    with pytest.raises(InvalidScheme):
        src = HTTPJar('https://aol.com/aol.tgz')
