import base64

import six

from .. import InlineBinary, InlineTarGZ, InlineText
from .. import interpret
from .. import HTTP, HTTPJar, HTTPTar, S3, S3Jar, S3Tar
from .inline import small_tgz


def test_url_dispatch():
    assert isinstance(interpret('http://pokemon.x.y/'), HTTP)
    assert isinstance(interpret('jar+https://pokemon.x.y/pika.jar'), HTTPJar)
    assert isinstance(interpret('tar+http://pokemon.x.y/rocket.tgz'), HTTPTar)

    assert isinstance(interpret('s3://pokemon/x.y'), S3)
    assert isinstance(interpret('jar+s3://pokemon.x.y/pika.jar'), S3Jar)
    assert isinstance(interpret('tar+s3://pokemon.x.y/rocket.tgz'), S3Tar)


def test_inline_dispatch():
    binary_tgz = base64.b64decode(small_tgz)

    assert isinstance(interpret({'text': 'a string'}), InlineText)
    assert isinstance(interpret({'data': six.b('binary')}), InlineBinary)
    assert isinstance(interpret({'tgz': binary_tgz}), InlineTarGZ)

    assert isinstance(interpret({'base64': 'YSBzdHJpbmc='}), InlineBinary)
    assert isinstance(interpret({'tgz64': small_tgz}), InlineTarGZ)
