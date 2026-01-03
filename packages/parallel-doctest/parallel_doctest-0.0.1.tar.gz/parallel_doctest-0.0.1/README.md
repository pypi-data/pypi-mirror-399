Parallel Doctest
================

Parallel Doctest splits doctests up and allows them to be
executed in parallel to help investigate concurrency bugs.
It is based on Python's standard-library ``doctest`` module.

Usage
-----

### Preparing tests

Parallel Doctest will first do a (crude) scan of your
doctest code to work out which individual tests within
a ``Doctest`` block depend on each other. For example
given a block::

    >>> a = 1
    >>> print(a)
    1
    >>> print(2)

The second line ``print(a)`` depends on the first line an thus should be run as a sequential series.

This is an automatic process although at this stage is fairly incomplete.

Tests can be marked as unsuitable for parallel execution with:

* ``# doctest: +NO_PARALLEL_MODULE`` disables parallel
  execution for the whole module.
* ``# doctest: +NO_PARALLEL_BLOCK`` disables parallel
  execution for a given block (i.e. everything in a function docstring).
* ``# doctest: +NO_PARALLEL`` disables parallel execution
  for that example only (i.e. just a single line starting
  with ``>>>``).

All these ``NO_PARALLEL`` directives disable parallelization for
the tests so that they will be the only test executing when they
are run.

Some control of serialization can be achieved with:

* ``# doctest: +SEQUENTIAL_BLOCK`` marks the whole block
  to be run in series. In this case the block may be run
  in parallel with other blocks but the individual tests
  in the block will be run in order.
* ``# doctest: +AFTER_PREVIOUS`` manually adds a dependency
  for an individual doctest so that it is only run after the
  previous one (which must be in the same block).

### Repeats

The number of repeats can be controlled with the option flags
``PARALLEL_REPEAT_1``, ``PARALLEL_REPEAT_2``, ``PARALLEL_REPEAT_4``,
going in factors of 2 up to ``PARALLEL_REPEAT_1024``. These are
intended to be enabled at the command-line rather than set in
doctested code.  To get (e.g.) 5 repeats use both ``PARALLEL_REPEAT_1``
and ``PARALLEL_REPEAT_4``.  Parallel repeats only apply to parallel
tests and not to any test that's serialized.

Alternatively the environmental variable ``PARALLEL_DOCTEST_REPEAT``
can be used to override it (and this takes priority).

### High level interface

Parallel Doctest can be used from the command-line in the same way
as the Python ``doctest`` module::

    python -m parallel_doctest -v example.py

Parallel Doctest also exposes the following high-level functions,
designed to match the Python ``doctest`` interface as much as possible::

``testmod(m=None, ...)`` - pass a module object and test all
the docstrings of functions and classes in the module.

``run_docstring_examples(f, ...)`` - pass a function, class, string, or module
and run all the doctests associated with that.

``testfile(filename, ...)`` - load examples from a filename.

### Unit test interface

Parallel Doctest doesn't expose the full ``unittest`` interface of ``doctest``
directly, but instead has one function:

``load_module_as_unittest_case(module)`` - loads all doctests from a module
into a single ``unittest.TestSuite``.

Commentary
----------

This tool was largely created to investigate thread-safety issues,
both with thread sanitizer and Python level. It is intended for that
rather than to try to speed up testing by parallelizing (which is
probably more likely to be a pessimization, even on free-threaded
builds of Python).

Most uses of ``doctest`` are for integration-level tests which may not
parallelize hugely well so be wary of that.  ``SEQUENTIAL_BLOCK`` is
probably a good default option to apply globally as a reasonable
compromise between getting some parallelization and avoiding too many
failures due to side-effects.

A lot of doctests are based heavily round console output (it is what
it tests, after all!). ``parallel-doctest`` solves this by redirecting
``sys.stdout`` and ``sys.stderr`` into thread-local variables.
This isn't expected to be hugely fast, so you may find your tests are
not doing too much parallel work.  For best results, try to run tests that
do real work with a small amount of output.