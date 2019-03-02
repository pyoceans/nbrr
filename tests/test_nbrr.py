import sys
import textwrap
from contextlib import contextmanager
from io import StringIO
from pathlib import Path

from nbrr.nbrr import _make_env_file, parse_notebook, parse_pyfiles

rootpath = Path(__file__).parent.absolute().joinpath("repo")


@contextmanager
def captured_output():
    new_out, new_err = StringIO(), StringIO()
    old_out, old_err = sys.stdout, sys.stderr
    try:
        sys.stdout, sys.stderr = new_out, new_err
        yield sys.stdout, sys.stderr
    finally:
        sys.stdout, sys.stderr = old_out, old_err


def test_parse_notebook():
    res = parse_notebook(rootpath.joinpath("notebook.ipynb"))
    assert res == ["matplotlib", "numpy", "pandas", "wget"]


def test_parse_pyfiles():
    res = parse_pyfiles(rootpath)
    assert res == ["matplotlib", "numpy", "pandas", "wget"]


def test__make_env_file():
    dependencies = ["matplotlib", "numpy", "pandas", "python-wget"]
    with captured_output() as (out, err):
        _make_env_file(dependencies, channels="conda-forge", name="TEST-ENV")

    expected = textwrap.dedent(
        """\
    name: TEST-ENV
    channels:
      - conda-forge
    dependencies:
      - matplotlib
      - numpy
      - pandas
      - python-wget"""
    )

    assert expected == out.getvalue().strip()
