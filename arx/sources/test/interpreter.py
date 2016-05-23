import base64

import six

from ..http import HTTP, HTTPJar, HTTPTar
from ..inline import InlineBinary, InlineTarGZ, InlineText
from ..interpreter import default
from ..s3 import S3, S3Jar, S3Tar
from .inline import small_tgz


def test_url_dispatch():
    assert isinstance(default('http://pokemon.x.y/'), HTTP)
    assert isinstance(default('jar+https://pokemon.x.y/pika.jar'), HTTPJar)
    assert isinstance(default('tar+http://pokemon.x.y/rocket.tgz'), HTTPTar)

    assert isinstance(default('s3://pokemon/x.y'), S3)
    assert isinstance(default('jar+s3://pokemon.x.y/pika.jar'), S3Jar)
    assert isinstance(default('tar+s3://pokemon.x.y/rocket.tgz'), S3Tar)


def test_inline_dispatch():
    binary_tgz = base64.b64decode(small_tgz)

    assert isinstance(default({'text': 'a string'}), InlineText)
    assert isinstance(default({'data': six.b('binary')}), InlineBinary)
    assert isinstance(default({'tgz': binary_tgz}), InlineTarGZ)

    assert isinstance(default({'base64': 'YSBzdHJpbmc='}), InlineBinary)
    assert isinstance(default({'tgz64': small_tgz}), InlineTarGZ)
