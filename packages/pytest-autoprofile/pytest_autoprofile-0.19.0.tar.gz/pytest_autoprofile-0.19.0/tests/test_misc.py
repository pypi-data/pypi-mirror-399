"""
Misc. tests that don't belong anywhere else.
"""
import re
import os
import pytest
import platform
import sys

from pytest_autoprofile._test_utils import propose_name, write_script
from pytest_autoprofile._typing import ImportPath


@pytest.mark.xfail(
    platform.system() == 'Windows',
    raises=ModuleNotFoundError,
    reason='Test known to flake on Windows (see issue #4)',
    strict=False,
)
def test_resolving_ambiguous_import_path(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path_factory: pytest.TempPathFactory,
) -> None:
    """
    Test that `~._typing.ImportPath.import_target(fuzzy=True)` raises an
    `ImportError` with an ambiguous target.

    FIXME
    -----
    Flakes on Windows (see issue #4);
    currently we just let it either XFAIL or XPASS since the integration
    tests using `ImportPath.import_target()` seems to work alright.
    """
    added_path = tmp_path_factory.mktemp('.packages')
    assert added_path.is_dir()
    monkeypatch.syspath_prepend(str(added_path))
    assert str(added_path) in sys.path
    mypkg_name = next(propose_name('my_ambiguous_pkg'))
    assert write_script(
        added_path / mypkg_name / '__init__.py',
        """
        from .util import Util


        util = Util()
        """,
    ).is_file()
    assert write_script(
        added_path / mypkg_name / 'util.py', 'class Util: pass',
    ).is_file()
    print(added_path, os.listdir(added_path))
    ipath1 = ImportPath(mypkg_name + '.util')
    ipath2 = ipath1.fuzzy[1]
    util_submod = ipath1.import_target()
    util_obj = ipath2.import_target()
    print(ipath1, '->', util_submod)
    print(ipath2, '->', util_obj)
    with pytest.raises(
        ImportError,
        match=re.escape(
            f'self = ImportPath({str(ipath1)!r}), fuzzy = True: '
            'ambiguous resolution (path(s) -> resolved): '
            f'{ipath1} -> {util_submod!r}, {ipath2} -> {util_obj!r}',
        ),
    ):
        ipath1.import_target(fuzzy=True)
