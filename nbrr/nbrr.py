import glob
import sys
import textwrap

import depfinder
import easyargs
from git import Repo
from ruamel.yaml import YAML

# list of packages that have different names from the PyPI-import name.
CONDA_NAMES = {"wget": "python-wget"}


# TODO: add extras like: jupyter, rise, etc.


def parse_notebook(fname):
    """Return the list of required dependencies for a notebook."""
    if str(fname).endswith(".ipynb"):
        dependencies = depfinder.notebook_path_to_dependencies(fname)[
            "required"
        ]
    else:
        raise ValueError(f"Cannot parse file {fname}.")
    return sorted(dependencies)


def parse_pyfiles(directory="."):
    """Return the list of required dependencies for all .py files in a directory."""
    deps = depfinder.main.simple_import_search(directory)
    dependencies = deps.get("required")
    return sorted(dependencies) if dependencies else []


def _find_notebooks(directory="."):
    return glob.iglob(f"{directory}/**/*.ipynb", recursive=True)


def _make_env_file(dependencies, channels, name):
    dependencies = [CONDA_NAMES.get(item, item) for item in dependencies]
    env = {"name": name, "channels": channels, "dependencies": dependencies}
    yaml = YAML()
    yaml.default_flow_style = False
    yaml.indent(offset=2)
    yaml.dump(env, sys.stdout)


def _get_repo(directory="."):
    repo = Repo(directory)
    origin = list(repo.remotes.origin.urls)[0]
    origin_url = origin.rsplit(".git", 1)[0]
    if origin_url.startswith("http"):
        return origin_url.rsplit("/", 2)[-2::]
    elif origin_url.startswith("git"):
        return origin_url.rsplit(":")[1].split("/")
    else:
        raise ValueError(f"Could not parse repository for {directory}.")


@easyargs
class NBRR(object):
    """Easy environment.yaml and README files for your notebook collection."""

    def env(self, directory=".", channels=["conda-forge"], name="my-env"):
        dependencies = parse_pyfiles(directory=directory)
        notebooks = _find_notebooks()
        for notebook in notebooks:
            dependencies.extend(parse_notebook(notebook))
        dependencies = sorted(set(dependencies))

        _make_env_file(dependencies=dependencies, channels=channels, name=name)

    def binder_badge(self, directory=".", notebook_path=None, branch="master"):
        user, repo = _get_repo(directory=".")
        url = f"https://mybinder.org/v2/gh/{user}/{repo}/{branch}"
        if notebook_path:
            url += f"?filepath={notebook_path}"

        return f"[http://mybinder.org/badge.svg]({url})"

    def travis(self, notebooks_path="notebooks"):
        return textwrap.dedent(
            f"""
            language: minimal

            sudo: false

            before_install:
              - wget http://bit.ly/miniconda -O miniconda.sh
              - bash miniconda.sh -b -p $HOME/miniconda
              - export PATH="$HOME/miniconda/bin:$PATH"
              - conda config --set always_yes yes --set changeps1 no --set show_channel_urls true
              - conda update conda
              # testing packages
              - conda create --name TEST --channel conda-forge nbval pytest

            install:
              - conda install --name TEST --file environment.yml
              - source activate TEST
              - conda info --all
              - conda list

            script:
              # The option `--nbval-lax` won't compare the notebooks cell results,
              # it will only run them! Use `--nbval` instead if you wish to validate outputs.
              pytest --nbval-lax -p no:python {notebooks_path} ;
            """
        )

    def appveyor(self, notebooks_path="notebooks"):
        return textwrap.dedent(
            f"""
            build: false

            environment:
              matrix:
                - PYTHON: "C:\\Miniconda36-x64"

            init:
              - "ECHO %PYTHON_VERSION% %MINICONDA%"

            install:
              - "set PATH=%PYTHON%;%PYTHON%\\Scripts;%PATH%"
              - conda config --set always_yes yes --set changeps1 no --set show_channel_urls true
              - conda update conda
              - conda install --name TEST --file environment.yml
              - activate TEST
              - conda info --all
              - conda list

            test_script:
              # The option `--nbval-lax` won't compare the notebooks cell results,
              # it will only run them! Use `--nbval` instead if you wish to validate outputs.
              - pytest --nbval-lax -p no:python {notebooks_path} ;
            """
        )


if __name__ == "__main__":
    NBRR()
