import doctest as _doctest

# If this applies to any of the doctests in the module, it isn't run in parallel
NO_PARALLEL_MODULE = _doctest.register_optionflag('NO_PARALLEL_MODULE')
# If this applies to any of the doctests in a block (e.g. function), they aren't run in parallel
NO_PARALLEL_BLOCK = _doctest.register_optionflag('NO_PARALLEL_BLOCK')
# Applies to a single doctest only
NO_PARALLEL = _doctest.register_optionflag('NO_PARALLEL')

# The block is run in series (but potentially in parallel with other blocks)
SEQUENTIAL_BLOCK = _doctest.register_optionflag('SEQUENTIAL_BLOCK')
# Manually add a dependency
AFTER_PREVIOUS = _doctest.register_optionflag('AFTER_PREVIOUS')

# Parallel repeats (specified in powers of 2 to let you generate a somewhat
# arbitrary number)
for _power_of_2 in range(11):
    _name = f'PARALLEL_REPEAT_{2**_power_of_2}'
    globals()[_name] = _doctest.register_optionflag(_name)