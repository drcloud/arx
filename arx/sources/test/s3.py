import pytest

from ...decorators import InvalidScheme
from ..http import HTTP, HTTPJar, HTTPTar
from ..s3 import S3, S3Jar, S3Tar, Invalid


def test_http():
    src = S3('s3://bucket/key')
    assert src.authority == 'bucket'
    assert src.path == '/key'
    assert src.fragment is None

    assert isinstance(src.sign(), HTTP)

    with pytest.raises(Invalid):
        src = S3('s3://bucket/key#pieces')

    with pytest.raises(InvalidScheme):
        src = S3('tar+s3://bucket/key')

    with pytest.raises(InvalidScheme):
        src = S3('jar+s3://bucket/key')


def test_tar():
    src = S3Tar('tar+s3://bucket/key.tbz')
    assert src.scheme == 'tar+s3'
    assert src.authority == 'bucket'
    assert src.path == '/key.tbz'

    assert isinstance(src.sign(), HTTPTar)

    with pytest.raises(InvalidScheme):
        src = S3Tar('https://aol.com/aol.tgz')


def test_jar():
    src = S3Jar('jar+s3://bucket/key.jar')
    assert src.scheme == 'jar+s3'
    assert src.authority == 'bucket'
    assert src.path == '/key.jar'
    assert src.fragment is None

    assert isinstance(src.sign(), HTTPJar)

    with pytest.raises(Invalid):
        S3Jar('jar+s3://bucket/key.jar#web.xml')

    with pytest.raises(InvalidScheme):
        src = S3Jar('tar+s3://bucket/key')

    with pytest.raises(InvalidScheme):
        src = S3Jar('https://aol.com/web.jar')
