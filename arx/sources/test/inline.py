import base64

import six

from ..inline import InlineBinary, InlineTarGZ, stringsafe


def test_stringsafe():
    binary = base64.b64decode(small_tgz)
    assert stringsafe(small_tgz)
    assert not stringsafe(binary)


def test_b64():
    text, encoded = ('a string', 'YSBzdHJpbmc=')
    assert base64.b64encode(six.b(text)).decode() == encoded
    source = InlineBinary.base64(encoded)
    assert isinstance(source, InlineBinary)
    assert six.b(text) == source.data


def test_b64_targz():
    source = InlineTarGZ.base64(small_tgz)
    assert isinstance(source, InlineTarGZ)


# Contains one file `x/x` with contents `x`.
small_tgz = """
    H4sIAFbACFcAA+3RSwrCMBSF4Tt2FdlBb9I81lOUgigKRiHLN9jSQSkdCEGE/5uc
    QUJykls6aU5VUwjmk3FKdX7KmbEuqbO+LvRGrYvWigntq4m88nN41Cr5fj2f8m04
    Xrb31W3juHPO/I4l/0TpSvM76n9E7/fm79bzT6kXo82bCfM//LoBAAAAAAAAAAAA
    AAAAgG+9AdEJedgAKAAA
"""
