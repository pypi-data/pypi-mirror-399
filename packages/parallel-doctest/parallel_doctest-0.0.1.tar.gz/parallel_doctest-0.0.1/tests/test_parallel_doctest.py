import unittest
import doctest
import io
from threading import Thread

import parallel_doctest
import parallel_doctest.details as details

class TestBlockSplitting(unittest.TestCase):
    def load_from_func(self, func):
        finder = doctest.DocTestFinder()
        found = finder.find(func)
        self.assertEqual(len(found), 1)
        return found[0]

    def test_all_self_contained(self):
        """
        >>> 1
        1
        >>> ...
        2
        >>> 3
        3
        >>> some_func()
        4
        """
        tests = self.load_from_func(self.test_all_self_contained)

        serial, parallel = details.calculate_doctest_independent_groups(tests)
        self.assertIsNone(serial)
        self.assertEqual(len(parallel), 4)
        for p in parallel:
            self.assertEqual(len(p.examples), 1)
            self.assertIn(p.examples[0], tests.examples)

    def test_serial(self):
        """
        >>> 1 # doctest: +NO_PARALLEL
        1
        >>> 2
        2
        """
        tests = self.load_from_func(self.test_serial)
        serial, parallel = details.calculate_doctest_independent_groups(tests)
        self.assertEqual(len(serial.examples), 1)
        self.assertEqual(len(parallel), 1)
        self.assertEqual(len(parallel[0].examples), 1)

    def test_simple_chains(self):
        def f1():
            """
            >>> a = 1
            >>> b = a
            >>> c = b
            """
        def f2():
            """
            >>> a = 1
            >>> b = a
            >>> c = a
            """
        def f3():
            """
            >>> a = 1
            >>> b = a
            >>> c = a*b
            """
        def f4():
            """
            >>> a = 1
            >>> b = 2
            >>> c = a*b
            """
        for f in [f1, f2, f3, f4]:
            with self.subTest(f.__name__):
                tests = self.load_from_func(f)
                serial, parallel = details.calculate_doctest_independent_groups(tests)
                self.assertIsNone(serial)
                self.assertEqual(len(parallel), 1)
                self.assertEqual(len(parallel[0].examples), 3)
                max_lineno = -99999
                for e in parallel[0].examples:
                    self.assertIn(e, tests.examples)
                    # Line numbers go up (so they're executed in order)
                    self.assertGreater(e.lineno, max_lineno)
                    max_lineno = max(max_lineno, e.lineno)

    def test_something_in_the_middle(self):
        """
        >>> a = 1
        >>> print("hello")
        hello
        >>> a
        1
        """
        tests = self.load_from_func(self.test_something_in_the_middle)
        serial, parallel = details.calculate_doctest_independent_groups(tests)
        self.assertIsNone(serial)
        self.assertEqual(len(parallel), 2)

    def test_serial_propagates(self):
        def f1():
            """
            >>> a = 1  # doctest: +NO_PARALLEL
            >>> b = a
            """
        def f2():
            """
            >>> a = 1
            >>> b = a  # doctest: +NO_PARALLEL
            """
        for f in [f1, f2]:
            with self.subTest(f.__name__):
                tests = self.load_from_func(f)
                serial, parallel = details.calculate_doctest_independent_groups(tests)
                self.assertEqual(len(parallel), 0)
                self.assertEqual(len(serial.examples), 2)

    def test_classes_and_functions(self):
        def f1():
            """
            >>> class C:
            ...    pass
            >>> print(C)
            """
        def f2():
            """
            >>> def call_me_maybe():
            ...    pass
            >>> print(call_me_maybe)
            """
        def f3():
            """
            >>> async def call_me_asynchronously_maybe():
            ...    pass
            >>> print(call_me_asynchronously_maybe)
            """
        for f in [f1, f2, f3]:
            with self.subTest(f.__name__):
                tests = self.load_from_func(f)
                serial, parallel = details.calculate_doctest_independent_groups(tests)
                self.assertEqual(serial, None)
                self.assertEqual(len(parallel), 1)
                self.assertEqual(len(parallel[0].examples), 2)

    def test_after_previous_bad(self):
        def bad():
            """
            >>> print(1) # doctest: +AFTER_PREVIOUS
            >>> print(2)
            """
        import io
        import sys

        tests = self.load_from_func(bad)
        old_stderr = sys.stderr
        sys.stderr = stderr = io.StringIO()
        try:
            serial, parallel = details.calculate_doctest_independent_groups(tests)
        finally:
            sys.stderr = old_stderr
        self.assertEqual(serial, None)
        self.assertEqual(len(parallel), 2)
        # We should definely warn
        self.assertTrue(
            stderr.getvalue().startswith(
                "Unable to use AFTER_PREVIOUS on first test in a block"),
            stderr.getvalue())
        
    def test_after_previous_good1(self):
        def f():
            """
            >>> print(1)
            >>> print(2) # doctest: +AFTER_PREVIOUS
            """

        def g():
            """
            >>> print(1)
            >>> print(2) # doctest: +AFTER_PREVIOUS
            >>> print(3)
            """

        def h():
            """
            >>> print(1)
            >>> print(2) # doctest: +AFTER_PREVIOUS
            >>> print(3) # doctest: +AFTER_PREVIOUS
            """

        def i():
            """
            >>> print(1)
            >>> print(2)
            >>> print(3) # doctest: +AFTER_PREVIOUS
            """

        for func in [f, g, h, i]:
            with self.subTest(func.__name__):
                tests = self.load_from_func(func)
                serial, parallel = details.calculate_doctest_independent_groups(tests)
                self.assertEqual(serial, None)

                if func == f or func == h:
                    self.assertEqual(len(parallel), 1)
                else:
                    self.assertEqual(len(parallel), 2)
                    if func == g:
                        self.assertIn(
                            "print(1)",
                            parallel[0].examples[0].source
                        )
                        self.assertIn(
                            "print(2)",
                            parallel[0].examples[1].source
                        )
                        self.assertIn(
                            "print(3)",
                            parallel[1].examples[0].source
                        )
                    if func == i:
                        self.assertIn(
                            "print(1)",
                            parallel[0].examples[0].source
                        )
                        self.assertIn(
                            "print(2)",
                            parallel[1].examples[0].source
                        )
                        self.assertIn(
                            "print(3)",
                            parallel[1].examples[1].source
                        )

    def test_after_previous_good2(self):
        def f():
            # Dependency (but it's fine - it agrees with AFTER_PREVIOUS)
            """
            >>> a = 1
            >>> print(a) # doctest: +AFTER_PREVIOUS
            """

        def g():
            # Note hidden dependency on the second test
            """
            >>> a = 1
            >>> print(globals()['a'])  # doctest: +AFTER_PREVIOUS
            >>> print(a)
            """
        
        for func in [f, g]:
            with self.subTest(func.__name__):
                tests = self.load_from_func(func)
                serial, parallel = details.calculate_doctest_independent_groups(tests)
                self.assertEqual(serial, None)
                self.assertEqual(len(parallel), 1)

    def test_sequential_block_noparallel(self):
        def f():
            """
            >>> f()
            >>> f()  # doctest: +SEQUENTIAL_BLOCK
            >>> f()  # doctest: +NO_PARALLEL
            """

        tests = self.load_from_func(f)
        serial, parallel = details.calculate_doctest_independent_groups(tests)
        self.assertEqual(len(parallel), 0)
        self.assertEqual(len(serial.examples), 3)

    def test_sequential_block(self):
        def f():
            """
            >>> f(0)
            >>> f(1)  # doctest: +SEQUENTIAL_BLOCK
            >>> f(2)
            """

        tests = self.load_from_func(f)
        serial, parallel = details.calculate_doctest_independent_groups(tests)
        self.assertIsNone(serial)
        self.assertEqual(len(parallel), 1)
        self.assertEqual(len(parallel[0].examples), 3)
        for n, e in enumerate(parallel[0].examples):
            self.assertIn(str(n), e.source)


class TestPerThreadOutput(unittest.TestCase):
    def do_write(self, id, out):
        print(f"Hello from {id}", file=out)
        return id, out.getvalue()
    
    def test_writing(self):
        out = details.PerThreadSpoofOut()
        results = []
        def operation(id):
            results.append(self.do_write(id, out))
        threads = [Thread(target=operation, args=(id,)) for id in range(20)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        results = sorted(results)
        for i in range(20):
            id, string = results[i]
            self.assertEqual(id, i)
            self.assertEqual(string, f"Hello from {id}\n")

    def test_truncate(self):
        out = details.PerThreadSpoofOut()
        results = []
        ids = list(range(20))
        def operation():
            while True:
                try:
                    id = ids.pop()
                except IndexError:
                    return  # done
                results.append(self.do_write(id, out))
                out.truncate(0)  # This is what doctest uses to reset it
        threads = [Thread(target=operation) for _ in range(4)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        results = sorted(results)
        for i in range(20):
            id, string = results[i]
            self.assertEqual(id, i)
            self.assertEqual(string, f"Hello from {id}\n")


class Overall(unittest.TestCase):
    def test_example(self):
        try:
            from .test_example import some_py_file
        except ImportError:
            from test_example import some_py_file
        suite = parallel_doctest.load_module_as_unittest_case(some_py_file)
        # redirect stream to keep the output clean
        runner = unittest.TextTestRunner(stream=io.StringIO())
        result = runner.run(suite)
        self.assertEqual(len(result.failures) + len(result.errors), 1)  # 1 deliberate error

    def test_serial_module(self):
        try:
            from .test_example import some_serial_module
        except ImportError:
            from test_example import some_serial_module
        
        suite = parallel_doctest.load_module_as_unittest_case(some_serial_module)
        # redirect stream to keep the output clean
        runner = unittest.TextTestRunner(stream=io.StringIO())
        result = runner.run(suite)
        self.assertEqual(len(result.failures) + len(result.errors), 0)

    def test_manual_sequencing(self):
        try:
            from .test_example import manual_sequencing
        except ImportError:
            from test_example import manual_sequencing
        suite = parallel_doctest.load_module_as_unittest_case(manual_sequencing)
        # redirect stream to keep the output clean
        runner = unittest.TextTestRunner(stream=io.StringIO())
        result = runner.run(suite)
        self.assertEqual(len(result.failures) + len(result.errors), 0)
        
    def test_testfile(self):
        import sys
        sys.stderr, original_stderr = io.StringIO(), sys.stderr
        try:
            failures, _ = parallel_doctest.testfile('test_example/some_txt_file.txt')
        finally:
            sys.stderr = original_stderr
        self.assertEqual(failures, 0)

    def test_testmod(self):
        import sys
        try:
            from .test_example import some_py_file
        except ImportError:
            from test_example import some_py_file
        sys.stderr, original_stderr = io.StringIO(), sys.stderr
        try:
            failures, _ = parallel_doctest.testmod(some_py_file)
        finally:
            sys.stderr = original_stderr
        self.assertEqual(failures, 1)  # 1 deliberate error


if __name__ == "__main__":
    unittest.main()