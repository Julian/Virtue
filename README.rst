======
Virtue
======

|PyPI| |Pythons| |CI| |ReadTheDocs| |Precommit|

.. |PyPI| image:: https://img.shields.io/pypi/v/Virtue.svg
  :alt: PyPI version
  :target: https://pypi.org/project/Virtue/

.. |Pythons| image:: https://img.shields.io/pypi/pyversions/Virtue.svg
  :alt: Supported Python versions
  :target: https://pypi.org/project/Virtue/

.. |CI| image:: https://github.com/Julian/Virtue/workflows/CI/badge.svg
  :alt: Build status
  :target: https://github.com/Julian/Virtue/actions?query=workflow%3ACI

.. |ReadTheDocs| image:: https://readthedocs.org/projects/virtue/badge/?version=stable&style=flat
  :alt: ReadTheDocs status
  :target: https://virtue.readthedocs.io/en/stable/

.. |Precommit| image:: https://results.pre-commit.ci/badge/github/Julian/Virtue/main.svg
   :alt: pre-commit.ci status
   :target: https://results.pre-commit.ci/latest/github/Julian/Virtue/main


``virtue`` is a modern, extensible,
`unittest <https://docs.python.org/3/library/unittest.html>`_ compliant
test runner.

It is *not* a test framework (it doesn't contain a ``TestCase`` subclass
and it never will).

Usage
-----

Running a ``unittest``-based suite works essentially as it does for
``twisted``'s ``trial``, i.e.::

    $ python -m virtue mypackage.tests

will run the tests subpackage of a given importable package.

More docs are coming. Sorry.


Contributing
------------

I'm Julian Berman.

``virtue`` is on `GitHub <http://github.com/Julian/Virtue>`_.

Get in touch, via GitHub or otherwise, if you've got something to contribute,
it'd be most welcome!

You can also generally find me on Libera (nick: ``Julian``) in various
channels, including ``#python``.

If you feel overwhelmingly grateful, you can also `sponsor me
<https://github.com/sponsors/Julian/>`_.
