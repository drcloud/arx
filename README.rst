=======
``arx``
=======

.. image:: https://travis-ci.org/drcloud/arx.svg?branch=master
    :target: https://travis-ci.org/drcloud/arx

`Arx` captures a pattern that cuts across Dockerfiles, Travis CI setups, the
"curl pipe to shell" craze and many other execution environments: using URLs
and source code references to specify a task to run.

To `Arx`, a task comprises ``code`` and ``data``, each of which can reference
URLs -- tarballs in S3, Git repositories or even files local to your
development machine. A simple and extensible Python library, `Arx` supports
task specification with YAML or JSON or via an object-oriented API. `Arx` is
indifferent to transports but provides utilities for working with tasks
published to Redis or S3.


------------
Arx Concepts
------------

* `Arx` organizes a task into ``code`` and ``data``.

* Both ``code`` and ``data`` can reference `Source`\s.

* The ``code`` is an array of tasks, each of which consists of a command word
  and arguments to the command. The command word can be a `Source` which, when
  downloaded, will be marked executable and run with the supplied arguments.

  .. code:: yaml

      code:
        # Downloads install script, marks it executable and runs it
        - https://raw.githubusercontent.com/Homebrew/install/master/install
        # Interpreted as execv array
        - [brew, install, mosh, tmux]

  .. code:: yaml

      code:
        # Remote-sourced scripts can have arguments, too.
        - [https://raw.githubusercontent.com/Homebrew/install/master/install,
           --full]


* The ``data`` is an array of `Source`\s which may, optionally, be mapped to
  paths. Without a mapping, the `Source` is retrieved and unpacked in the
  temporary directory where code is executed. With a mapping, the `Source` is
  placed in the path given. This path can be an absolute reference to a
  location on the file system, a reference relative to the user's home
  directory, or a relative reference treating the temporary working directory
  as the present directory.

* A `Source` is a URL and can provide a single file or a file hierarchy. For
  example, an ``http://...`` source refernces a single file, the bytes returned
  from hitting that URL. A ``tar+http://...`` URL references a whole collection
  of files.


------------------
More About Sources
------------------

Arx sources are RFC 3986 URLs that point to files or collections of files. Each
source type, or URL scheme, can be understood as a class that implements three
methods:

* ``cache()``, which looks up the URL and copies it locally.

* ``place(path: FilePath)``, which takes the URL data obtained by ``cache`` and
  any fragment information attached to the URL and uses that to unpack the file
  contents somewhere.

* ``run(args: [CString])`` which treats the URL as an executable (if it refers
  to a single file) and runs it.

Some schemes are singular, like ``http`` sources, and some are plural, like
``git+ssh`` source. When a source is plural, Arx allows the use of a fragment
identifier to select a particular file (which casts to singular) or a
particular subdirectory (by ending the frament with a slash).

Arx natively understands several URL types.

* ``http``, ``https`` -- Singular.

* ``git+ssh``, ``git+http``, ``git+https`` -- Plural.

* ``dir`` -- A local directory reference. Plural. The data can be inlined into
  the task to allow for remote execution.

* ``file`` -- A local file reference. Singular. The file data can be inlined
  into the task to allow for remote execution.

* ``s3`` -- This one is more complicated than most. If it ends with a slash,
  it is plural; if not, singular. In the singular form, the URL can be signed
  and converted into an HTTP URL.

* ``jar+http``, ``jar+https``, ``jar+s3``, ``jar+file`` -- Singular. Executed
  with ``java -jar ...``.

* ``tar+http``, ``tar+https``, ``tar+s3``, ``tar+file`` -- Plural. The special
  fragment ``#//`` collapes the top level directory.


-------
Testing
-------

Run ``tox`` or ``make test``.
