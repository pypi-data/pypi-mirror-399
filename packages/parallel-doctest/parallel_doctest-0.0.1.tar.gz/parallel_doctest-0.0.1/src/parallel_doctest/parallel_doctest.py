import doctest
import unittest
import inspect
import io
import sys
import os
from . import details

def _make_results(results):
    try:
        return doctest.TestResults(
            len(results.failures)+len(results.errors),
            results.testsRun,
            skipped=len(results.skipped)
        )
    except TypeError as e:
        if "unexpected keyword argument 'skipped'" in e.args[0]:
            # Not in older Python versions
            return doctest.TestResults(
                len(results.failures)+len(results.errors),
                results.testsRun
            )
        raise

def load_module_as_unittest_case(module):
    finder = doctest.DocTestFinder()

    tests = finder.find(module)
    return details.process_module_doctests(tests, module_file=module.__file__)

def testmod(m=None, name=None, globs=None, verbose=None,
            report=True, optionflags=0, extraglobs=None,
            raise_on_error=False, exclude_empty=False):
    if raise_on_error:
        raise NotImplementedError("raise_on_error is not currently understood")
    
    # Taken from doctest
    if m is None:
        m = sys.modules.get('__main__')
    if not inspect.ismodule(m):
        raise TypeError("testmod: module required; %r" % (m,))
    if name is None:
        name = m.__name__

    finder = doctest.DocTestFinder(exclude_empty=exclude_empty)
    tests = finder.find(m, name, globs=globs, extraglobs=extraglobs)
    suite = details.process_module_doctests(tests, m.__file__, optionflags=optionflags)

    runner = unittest.TextTestRunner(
        verbosity=2 if verbose else 1,
        stream=sys.stderr if report else io.StringIO())
    return _make_results(runner.run(suite))

def testfile(filename, module_relative=True, name=None, package=None,
             globs=None, verbose=None, report=None, optionflags=0,
             extraglobs=None, raise_on_error=False, parser=doctest.DocTestParser(),
             encoding=None):
    if raise_on_error:
        raise NotImplementedError("raise_on_error is not currently understood")
    if report is not None:
        raise NotImplementedError("report is not implemented")
    if package and not module_relative:
        raise ValueError("Package may only be specified for module-"
                         "relative paths.")

    # Relativize the path
    text, filename = doctest._load_testfile(filename, package, module_relative,
                                    encoding or "utf-8")

    # If no name was given, then use the file's name.
    if name is None:
        name = os.path.basename(filename)

    # Assemble the globals.
    if globs is None:
        globs = {}
    else:
        globs = globs.copy()
    if extraglobs is not None:
        globs.update(extraglobs)
    if '__name__' not in globs:
        globs['__name__'] = '__main__'

    test = parser.get_doctest(text, globs, name, filename, 0)
    suite = details.process_module_doctests([test], name, optionflags=optionflags)

    runner = unittest.TextTestRunner(
        verbosity=2 if verbose else 1,
        stream=sys.stderr)
    return _make_results(runner.run(suite))


def run_docstring_examples(f, globs, verbose=False, name="NoName",
                           compileflags=None, optionflags=0):
    if compileflags:
        raise NotImplementedError("'compileflags' is not currently supported")

    finder = doctest.DocTestFinder(verbose=verbose, recurse=False)
    tests = finder.find(f, name, globs=globs)
    # not strictly a module, but this will still work
    suite = details.process_module_doctests(tests, name, optionflags=optionflags)

    runner = unittest.TextTestRunner(
        verbosity=2 if verbose else 1,
        stream=sys.stderr)
    return _make_results(runner.run(suite))
