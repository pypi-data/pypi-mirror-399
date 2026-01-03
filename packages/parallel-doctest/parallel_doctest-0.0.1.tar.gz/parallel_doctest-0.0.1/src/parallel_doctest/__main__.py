from .parallel_doctest import testmod, testfile
from doctest import _test
import types

new_globals = _test.__globals__.copy()
new_globals.update(
    testmod=testmod,
    testfile=testfile
)
new_test = types.FunctionType(
    code=_test.__code__,
    globals=new_globals,
    name=_test.__name__
)

new_test()