import glob
import sys
import textwrap

import depfinder
import easyargs
from git import Repo
from ruamel.yaml import YAML

# list of packages that have different names from the PyPI-import name.
CONDA_NAMES = {"wget": "python-wget"}


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
    channels = channels.split(",")
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


def _binder_badge(repository=".", notebook_path=None, branch="master"):
    user, repo = _get_repo(directory=repository)
    url = f"https://mybinder.org/v2/gh/{user}/{repo}/{branch}"
    badge = "![Binder](https://img.shields.io/badge/launch-binder-579aca.svg?logo=data:image/png;base64,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)"  # noqa
    if notebook_path:
        url += f"?filepath={notebook_path}"

    return f"[{badge}]({url})"


@easyargs
class NBRR(object):
    """Easy environment.yaml and README files for your notebook collection."""

    def env(
        self, directory=".", channels="conda-forge,defaults", name="my-env"
    ):
        dependencies = parse_pyfiles(directory=directory)
        notebooks = _find_notebooks()
        for notebook in notebooks:
            dependencies.extend(parse_notebook(notebook))
        dependencies = sorted(set(dependencies))

        _make_env_file(dependencies=dependencies, channels=channels, name=name)

    def travis(self, notebooks_path="notebooks"):
        yml = textwrap.dedent(
            f"""\
            language: minimal

            sudo: false

            matrix:
              include:
                - name: "linux"
                  os: linux
                - name: "osx"
                  os: osx

            before_install:
              # Install and configure miniconda.
              - |
                if [ "$TRAVIS_OS_NAME" == "osx" ]; then
                  URL="https://repo.continuum.io/miniconda/Miniconda3-latest-MacOSX-x86_64.sh"
                elif [ "$TRAVIS_OS_NAME" == "linux" ] ; then
                  URL="https://repo.continuum.io/miniconda/Miniconda3-latest-Linux-x86_64.sh"
                fi
                wget $URL -O miniconda.sh
                echo ""
                bash miniconda.sh -b -p $HOME/miniconda
                export PATH="$HOME/miniconda/bin:$PATH"
                conda config --set always_yes yes --set changeps1 no --set show_channel_urls true
                conda update conda --quiet
                conda config --add channels conda-forge --force
                conda install pycryptosat
                conda config --set sat_solver pycryptosat
                conda config --set safety_checks disabled
                conda config --set channel_priority strict

            install:
              # Create the test env.
              - |
                conda env create --file environment.yml --name TEST
                conda install --name TEST --channel conda-forge nbval pytest
                source activate TEST

              # Debug.
              - conda info --all
              - conda list

            script:
              # The option `--nbval-lax` won't compare the notebooks cell results,
              # it will only run them! Use `--nbval` instead if you wish to validate outputs.
              - pytest --nbval-lax -p no:python {notebooks_path}
            """
        )
        sys.stdout.writelines(yml)

    def appveyor(self, notebooks_path="notebooks"):
        yml = textwrap.dedent(
            f"""\
            build: false

            environment:
              matrix:
                - PYTHON: "C:\\\Miniconda36-x64"

            init:
              - "ECHO %PYTHON_VERSION% %MINICONDA%"

            install:
              # Install and configure miniconda.
              - "set PATH=%PYTHON%;%PYTHON%\\\Scripts;%PATH%"
              - conda config --set always_yes yes --set changeps1 no --set show_channel_urls true
              - conda update conda --quiet

              # Create the test env.
              - conda env create --file environment.yml --name TEST
              - conda install --name TEST --channel conda-forge nbval pytest
              - activate TEST

              # Debug.
              - conda info --all
              - conda list

            test_script:
              # The option `--nbval-lax` won't compare the notebooks cell results,
              # it will only run them! Use `--nbval` instead if you wish to validate outputs.
              - pytest --nbval-lax -p no:python {notebooks_path}
            """
        )
        sys.stdout.writelines(yml)

    def readme(
        self,
        title,
        repository=".",
        notebook_path=None,
        branch="master",
        travis="com",
    ):
        shield = "https://img.shields.io"
        user, repo = _get_repo(directory=repository)
        appveyor = repo.replace("_", "-").replace(".", "-")

        binder = _binder_badge(
            repository=repository, notebook_path=notebook_path, branch=branch
        )

        if travis == "com":
            travis_badge = "travis/com"
        elif travis == "org":
            travis_badge = "travis"
        else:
            raise ValueError(
                f"Unrecognized travis format. It should be `com` or `org` got {travis}."
            )

        txt = textwrap.dedent(
            f"""\
            # {title}

            ## Continuous Integration Tests

            | Platform        | Status                                                                                                                                              |
            | --------------- | --------------------------------------------------------------------------------------------------------------------------------------------------- |
            | Linux and macOS | [![Travis]({shield}/{travis_badge}/{user}/{repo}/{branch}.svg?label=Linux/macOS)](https://travis-ci.{travis}/{user}/{repo})                         |
            | Windows         | [![AppVeyor]({shield}/appveyor/ci/{user}/{appveyor}/{branch}.svg?label=Windows)](https://ci.appveyor.com/project/{user}/{appveyor}/branch/{branch}) |

            ## Binder

            {binder}
            """
        )
        sys.stdout.writelines(txt)


if __name__ == "__main__":
    NBRR()
