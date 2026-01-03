from hrenpack.python import import_all_submodules

"""
hrenpack_dir = Path(__file__).parent

for module in hrenpack_dir.glob('*.py'):
    if module.name == '__init__':
        continue
    import_module(f'.{module.stem}', package=__package__)
"""

import_all_submodules(__name__)
