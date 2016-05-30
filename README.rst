=======
``arx``
=======

.. image:: https://travis-ci.org/drcloud/arx.svg?branch=master
    :target: https://travis-ci.org/drcloud/arx

Arx captures a pattern common to Dockerfiles, CI setups, the ``curl ... | sh``
craze and many other execution environments: using URLs and source code
references to specify a runnable task.

Arx offers both a simple serialization format (leveraging the JSON-compatible
subset of YAML) and a programmatic API.

-------
Testing
-------

Run ``tox`` to test Arx.
