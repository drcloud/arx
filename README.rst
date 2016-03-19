=======
``arx``
=======

`Arx` captures a pattern that cuts across Dockerfiles, Travis CI setups, the
"curl pipe to shell" craze and many other execution environments: using URLs and source code references to specify a task to run.

To `Arx`, a task comprises ``code`` and ``data``, each of which can
reference URLs -- tarballs in S3, Git repositories or even files to inline. A
simple and extensible Python library, `Arx` supports task specification with
YAML or JSON or via an object-oriented API. `Arx` is indifferent to
transports but provides utilities for working with tasks published to Redis or
S3.

-------
Testing
-------

Run ``tox`` or ``make test``.
