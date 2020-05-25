======
Virtue
======

|PyPI| |Pythons| |CI| |Codecov| |ReadTheDocs|

.. |PyPI| image:: https://img.shields.io/pypi/v/Virtue.svg
  :alt: PyPI version
  :target: https://pypi.org/project/Virtue/

.. |Pythons| image:: https://img.shields.io/pypi/pyversions/Virtue.svg
  :alt: Supported Python versions
  :target: https://pypi.org/project/Virtue/

.. |CI| image:: https://github.com/Julian/Virtue/workflows/CI/badge.svg
  :alt: Build status
  :target: https://github.com/Julian/Virtue/actions?query=workflow%3ACI

.. |Codecov| image:: https://codecov.io/gh/Julian/Virtue/branch/master/graph/badge.svg
  :alt: Codecov Code coverage
  :target: https://codecov.io/gh/Julian/Virtue

.. |ReadTheDocs| image:: https://readthedocs.org/projects/virtue/badge/?version=stable&style=flat
  :alt: ReadTheDocs status
  :target: https://virtue.readthedocs.io/en/stable/


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

You can also generally find me on Freenode (nick: ``tos9``) in various
channels, including ``#python`` and ``#python-testing``.

If you feel overwhelmingly grateful, you can also woo me with beer money
via GitHub Sponsors above.
