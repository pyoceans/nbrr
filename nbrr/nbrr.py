"""Bootstrap a GitHub repository for reproducible Jupyter notebooks."""

import inspect
import sys
from collections.abc import Iterator
from pathlib import Path

import depfinder
import easyargs
from git import Repo
from ruamel.yaml import YAML

# list of packages that have different names from the PyPI-import name.
CONDA_NAMES = {"wget": "python-wget"}

OptionalStr = str | None


def parse_notebook(fname: str) -> list:
    """Return the list of required dependencies for a notebook."""
    if str(fname).endswith(".ipynb"):
        dependencies = depfinder.notebook_path_to_dependencies(fname)[
            "required"
        ]
    else:
        msg = f"Cannot parse file {fname}."
        raise ValueError(msg)
    return dependencies


def parse_pyfiles(directory: str = ".") -> list:
    """Return the list of required dependencies for all Python files
    in a directory.
    """
    deps = depfinder.main.simple_import_search(directory)
    dependencies = deps.get("required")
    return dependencies if dependencies else []


def _find_notebooks(directory: str = ".") -> Iterator:
    """Find all notebooks in a given directory recursively."""
    rootpath = Path(directory)
    return rootpath.rglob("**/*.ipynb")


def _make_env_file(
    dependencies: list,
    channels: str,
    name: str,
    extras: OptionalStr = None,
) -> None:
    """Create environment.yaml file."""
    if extras:
        extras = extras.split(",")
        dependencies.extend(extras)
    dependencies = [CONDA_NAMES.get(item, item) for item in dependencies]
    dependencies = sorted(set(dependencies))
    channels = channels.split(",")
    env = {"name": name, "channels": channels, "dependencies": dependencies}
    yaml = YAML()
    yaml.default_flow_style = False
    yaml.indent(offset=2)
    yaml.dump(env, sys.stdout)


def _get_repo(repository: str = ".") -> Exception:
    repo = Repo(repository)
    origin = next(iter(repo.remotes.origin.urls))
    origin_url = origin.rsplit(".git", 1)[0]
    if origin_url.startswith("http"):
        return origin_url.rsplit("/", 2)[-2::]
    if origin_url.startswith("git"):
        return origin_url.rsplit(":")[1].split("/")
    msg = f"Could not parse repository for {repository}."
    raise ValueError(msg)


def _binder_badge(
    repository: str = ".",
    notebook_path: OptionalStr = None,
    branch: str = "main",
) -> str:
    """Make binder badge."""
    user, repo = _get_repo(repository=repository)
    url = f"https://mybinder.org/v2/gh/{user}/{repo}/{branch}"
    badge = r"![Binder](https://mybinder.org/badge_logo.svg)"
    if notebook_path:
        url += f"?filepath={notebook_path}"

    return f"[{badge}]({url})"


@easyargs
class NBRR:
    """Easy environment.yml and README files for your notebook collection."""

    def env(
        self,
        extras: str = "python",
        directory: str = ".",
        channels: str = "conda-forge,defaults",
        name: str = "my-env",
    ) -> None:
        """Create environment.yml file."""
        dependencies = parse_pyfiles(directory=directory)
        notebooks = _find_notebooks()
        for notebook in notebooks:
            dependencies.extend(parse_notebook(notebook))
        # Jupyter is hardcoded b/c nbrr is designed for notebooks after all ;-p
        dependencies.append("jupyter")
        dependencies = sorted(set(dependencies))
        _make_env_file(
            dependencies=dependencies,
            channels=channels,
            name=name,
            extras=extras,
        )

    def readme(
        self,
        title: str,
        repository: str = ".",
        notebook_path: OptionalStr = None,
        branch: str = "main",
    ) -> str:
        """Create README file."""
        user, repo = _get_repo(repository=repository)

        binder = _binder_badge(
            repository=repository,
            notebook_path=notebook_path,
            branch=branch,
        )

        txt = inspect.cleandoc(
            rf"""
            # {title}

            ## Binder

            {binder}
            """,
        )
        sys.stdout.writelines(txt)


if __name__ == "__main__":
    NBRR()
