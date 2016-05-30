.. Arx documentation master file, created by
   sphinx-quickstart on Sat May 28 11:26:08 2016.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

=======
``arx``
=======

Arx offers a structured approach to combining data files from disparate
sources with commands to run against them, in a structured, auditable,
repeatable way. It draws inspiration from `Dockerfiles`_ and `Cloud Config`_
and (even) ``curl ... | sh``.

.. _Dockerfiles: https://docs.docker.com/engine/reference/builder/

.. _Cloud Config: http://cloudinit.readthedocs.io/en/latest/topics/examples.html


Arx is built around four core data types:

* :class:`~arx.bundle.Bundle`

* :class:`~arx.sources.core.Source`

* :class:`~arx.bundle.Code`

* :class:`~arx.bundle.Data`

A :class:`~arx.bundle.Bundle` is built from :class:`~arx.bundle.Code`\s and
:class:`~arx.bundle.Data`\s, which themselves reference
:class:`~arx.sources.core.Source`\s. A :class:`~arx.sources.core.Source` can
reference local files, inline data or a URL. Sources can have *file* or
*archive* nature: a Git repository has an archive nature while a direct HTTP
reference has a file nature.

The Arx API provides for flexible reading and writing of bundles and direct,
programmatic construction thereof. Running, repacking and auditing bundles can
be performed from the command line or through the Arx API.

~~~~~~~~~~
An Example
~~~~~~~~~~

Consider a from-source deployment of a web application. Maybe our application
is hosted on GitHub, it's Nginx configuration is separatelym maintained, and it
needs an internal secretes file. In Arx, it looks like this:

.. code:: yaml

    code:
      - [sh, -c, 'service app stop ; service app start']
      - [sh, -c, 'service nginx stop ; service nginx start']
    data:
      - /srv/app: git+ssh://github.com/examplecom/app.git
      - /etc/nginx: git+ssh://github.com/examplecom/sys.git#nginx
      - /etc/default/app: https://secrets.internal.example.com/generate/env

Or:

.. code:: python

    from arx import arx

    b = arx.Bundle(
        arx.Code('sh', '-c', 'service app stop ; service app start'),
        arx.Code('sh', '-c', 'service nginx stop ; service nginx start'),
        arx.Data('git+ssh://github.com/examplecom/app.git', '/srv/app'),
        arx.Data('git+ssh://github.com/examplecom/sys.git#nginx', '/etc/nginx'),
        arx.Data('https://secrets.internal.example.com/generate/env',
                 '/etc/default/app'),
    )

Calling ``b.run()`` (or ``arx /path/to/arx.yaml``) will step through all
the data, unpacking it to the specified locations, and then run the two
commands specified with `~arx.bundle.Code` (or in YAML, ``code``).


==================
Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`

