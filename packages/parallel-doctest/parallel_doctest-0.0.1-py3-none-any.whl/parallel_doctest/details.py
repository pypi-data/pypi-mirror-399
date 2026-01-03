import ast
import sys
import doctest
import types
import unittest
import io
import os
from concurrent.futures import ThreadPoolExecutor
from functools import wraps, lru_cache
from threading import local as ThreadLocal

from .directives import *

class FindTargets(ast.NodeVisitor):
    def __init__(self):
        self.targets = []

    def visit_Name(self, node):
        if isinstance(node.ctx, (ast.Store, ast.Del)):
            self.targets.append(node.id)

    def visit_ClassDef(self, node):
        self.targets.append(node.name)
        self.generic_visit(node)
    
    def visit_FunctionDef(self, node):
        self.targets.append(node.name)
        self.generic_visit(node)

    def visit_AsyncFunctionDef(self, node):
        self.targets.append(node.name)
        self.generic_visit(node)

class FindDependentNames(ast.NodeVisitor):
    def __init__(self):
        self.dependent_names = []

    def visit_Name(self, node):
        if isinstance(node.ctx, ast.Load):
            self.dependent_names.append(node.id)

def find_targets(tree):
    finder = FindTargets()
    finder.visit(tree)
    return finder.targets

def find_dependent_names(tree):
    finder = FindDependentNames()
    finder.visit(tree)
    return finder.dependent_names

def process_example_dependencies(example, dependencies, reversed_dependencies, seen):
    if example in seen:
        return None
    seen.add(example)
    linked_examples = [example]
    example_dependencies = dependencies.get(example, [])
    for dep in example_dependencies:
        dep_result = process_example_dependencies(dep, dependencies, reversed_dependencies, seen)
        if dep_result is not None:
            linked_examples.extend(dep_result)
    example_reversed_dependencies = reversed_dependencies.get(example, [])
    for rdep in example_reversed_dependencies:
        rdep_result = process_example_dependencies(rdep, dependencies, reversed_dependencies, seen)
        if rdep_result is not None:
            linked_examples.extend(rdep_result)
    return linked_examples

def calculate_doctest_independent_groups(doctest_: doctest.DocTest, optionflags=0):
    """
    Returns a length 2 tuple:
    [0] a doctest.DocTest object to be run in series (or None)
    [1] a list of doctest.DocTest objects that can be run in parallel
        (but the examples in each list element should be run sequentially)
    """

    if (optionflags & SEQUENTIAL_BLOCK) or any(
        e.options.get(SEQUENTIAL_BLOCK, False) for e in doctest_.examples
    ):
        if (optionflags & NO_PARALLEL) or any(
            e.options.get(NO_PARALLEL, False) for e in doctest_.examples
        ):
            # If block is serialized, and anything in the block is "NO_PARALLEL"
            # then I guess everything in the block has to be.
            return doctest_, []
        return None, [doctest_]*_calculate_parallel_repeats(optionflags)

    if optionflags & AFTER_PREVIOUS:
        print("Global option flag AFTER_PREVIOUS is ignored.", file=sys.stderr)

    existing_targets = {}
    dependencies = {}  # meaning "key" depends on this list of values
    for n, e in enumerate(doctest_.examples):
        tree = ast.parse(e.source)
        if e.options.get(AFTER_PREVIOUS, False):
            if n > 0:
                dependencies.setdefault(e, []).append(doctest_.examples[n-1])
            else:
                print("Unable to use AFTER_PREVIOUS on first test in a block", file=sys.stderr)
        dependent_names = find_dependent_names(tree)
        for name in dependent_names:
            if name in existing_targets:
                dependencies.setdefault(e, []).extend(existing_targets[name])
        targets = find_targets(tree)
        for name in targets:
            existing_targets.setdefault(name, []).append(e)

    # meaning "key" is depended on this list of values
    reversed_dependencies = {}
    for k, values in dependencies.items():
        for v in values:
            reversed_dependencies.setdefault(v, []).append(k)

    independent_blocks = []
    seen = set()
    for e in doctest_.examples:
        linked_examples = process_example_dependencies(e, dependencies, reversed_dependencies, seen)
        if linked_examples is not None:
            independent_blocks.append(linked_examples)

    sequential_tests = []
    parallel_tests = []
    for block in independent_blocks:
        if ((optionflags & NO_PARALLEL) or
                any(e.options.get(NO_PARALLEL, False) for e in block)):
            sequential_tests.extend(block)
        else:
            blocks = [block]*_calculate_parallel_repeats(optionflags)
            parallel_tests.extend(blocks)
    sequential_tests.sort(key=lambda e: e.lineno)
    for parallel_block in parallel_tests:
        parallel_block.sort(key=lambda e: e.lineno)

    def convert_back_to_doctest(example_group):
        if not example_group:
            return None
        return doctest.DocTest(
            examples=example_group,
            globs=doctest_.globs,
            name=doctest_.name,
            filename=doctest_.filename,
            lineno=doctest_.lineno,
            docstring=doctest_.docstring
        )

    return (
        convert_back_to_doctest(sequential_tests),
        [convert_back_to_doctest(group) for group in parallel_tests]
    )


def _add_serial_tests(testSuite, tests, module_file: str, optionflags=0):
    # largely copied from DocTestSuite
    for test in tests:
        if len(test.examples) == 0:
            continue
        if not test.filename:
            filename = module_file
            if filename[-4:] == ".pyc":
                filename = filename[:-1]
            test.filename = filename
        testSuite.addTest(doctest.DocTestCase(test, optionflags=optionflags))


class GiantParallelTestCase(unittest.TestCase):
    def __init__(self, parallel_cases, max_workers=None, optionflags=0):
        self.fakeout = PerThreadSpoofOut()
        self.parallel_cases = [
            ParallelDocTestCase(t, shared_fakeout=self.fakeout, optionflags=optionflags)
            for t in parallel_cases
        ]
        self.max_workers = max_workers

    def run(self, result=None):
        if result is None:
            result = self.defaultTestResult()
        # The individual test runners will also do this but they'll all use
        # the same shared fake output object so it won't matter.
        original_stdout = sys.stdout
        sys.stdout = self.fakeout
        try:
            with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                results = executor.map(
                    lambda tc: tc.run(),
                    self.parallel_cases
                )
        finally:
            sys.stdout = original_stdout
        for r in results:
            for e in r.errors:
                result.errors.append(e)
            for f in r.failures:
                result.failures.append(f)
            # addSuccess does nothing by default
            for s in r.skipped:
                result.addSkip(*s)
            for ef in r.expectedFailures:
                result.addExpectedFailure(*ef)
            for us in r.unexpectedSuccesses:
                result.addUnexpectedSuccess(*us)
            # Durations only exist in Py3.12 and up
            result.testsRun += r.testsRun


class PerThreadSpoofOut(io.TextIOBase):
    original_spoof_out = doctest._SpoofOut

    def __init__(self, *args, **kwds):
        super().__init__(*args, **kwds)
        self.state = ThreadLocal()

    def get_per_thread_spoof_out(self):
        try:
            out = self.state.spoof_out
        except AttributeError:
            out = self.state.spoof_out = self.original_spoof_out()
        return out

    @staticmethod
    def _wrap_function(f):
        @wraps(f)
        def wrapper(self, *args, **kwds):
            out = self.get_per_thread_spoof_out()
            return f(out, *args, **kwds)
        return wrapper


    for attr in [# IOBase
                 "fileno", "seek", "truncate",
                 # TextIOBase
                 "detach", "read", "readline", "write",
                 # StringIO
                 "getvalue"]:
        locals()[attr] = _wrap_function(getattr(original_spoof_out, attr))


class ParallelDocTestCase(doctest.DocTestCase):
    def __init__(self, *args, shared_fakeout, **kwds):
        super().__init__(*args, **kwds)

        def make_doc_test_runner(*args, **kwds):
            runner = doctest.DocTestRunner(*args, **kwds)
            runner._fakeout = shared_fakeout
            return runner

        new_globals = doctest.DocTestCase.runTest.__globals__.copy()
        new_globals['DocTestRunner'] = make_doc_test_runner
        self.originalRunTest = types.FunctionType(
            code=doctest.DocTestCase.runTest.__code__,
            globals=new_globals,
            name=doctest.DocTestCase.runTest.__name__
        )

    def runTest(self):
        self.originalRunTest(self)


def process_module_doctests(tests: list[doctest.DocTest], module_file: str, optionflags=0):
    out = unittest.TestSuite()

    if ((optionflags & NO_PARALLEL_MODULE) or
            any(any(e.options.get(NO_PARALLEL_MODULE, False) for e in t.examples) for t in tests)):
        _add_serial_tests(out, tests, module_file, optionflags=optionflags)
        return out
    
    parallel_blocks : list[doctest.DocTest] = []
    for t in tests:
        if (optionflags & NO_PARALLEL_BLOCK) or any(e.options.get(NO_PARALLEL_BLOCK, False) for e in t.examples):
            _add_serial_tests(out, [t], module_file, optionflags=optionflags)
        else:
            parallel_blocks.append(t)

    parallel_tests = []
    for t in parallel_blocks:
        serial, parallel = calculate_doctest_independent_groups(t, optionflags=optionflags)
        if serial is not None:
            _add_serial_tests(out, [serial], module_file, optionflags=optionflags)
        parallel_tests.extend(parallel)
    out.addTest(
        GiantParallelTestCase(parallel_tests, optionflags=optionflags)
    )
    return out

@lru_cache
def _calculate_parallel_repeats(optionflags):
    env_var = os.environ.get('PARALLEL_DOCTEST_REPEATS')
    if env_var is not None:
        return int(env_var)

    repeats = 0

    for k, v in doctest.OPTIONFLAGS_BY_NAME.items():
        if not k.startswith('PARALLEL_REPEAT_'):
            continue
        try:
            k = int(k[len('PARALLEL_REPEAT_'):])
        except ValueError:
            continue
        
        if optionflags & v:
            repeats += k

    if repeats == 0:
        return 1
    return repeats
    