import glob
import sys

import depfinder

import easyargs

from ruamel.yaml import YAML


def binder_url(user, repo):
    # from github import Github
    # g = Github()
    # http://mybinder.org/badge.svg
    return f'https://mybinder.org/v2/gh/{user}/{repo}/master'


def parse_notebook(fname):
    """Return the list of required dependencies for a notebook."""
    if fname.endswith('.ipynb'):
        dependencies = depfinder.notebook_path_to_dependencies(fname)['required']
    else:
        raise ValueError(f'Cannot parse file {fname}.')
    return sorted(dependencies)


def parse_pyfiles(directory='.'):
    """Return the list of required dependencies for all .py files in a directory."""
    deps = depfinder.main.simple_import_search(directory)
    dependencies = deps.get('required')
    return sorted(dependencies) if dependencies else []


def _find_notebooks(directory='.'):
    return (glob.iglob(f'{directory}/**/*.ipynb', recursive=True))


def make_env_file(dependencies, channels, name):
    # TODO: add a list pip dependencies options.
    env = {
        'name': name,
        'channels': channels,
        'dependencies': dependencies
    }
    yaml = YAML()
    yaml.default_flow_style = False
    yaml.indent(offset=2)
    yaml.dump(env, sys.stdout)


@easyargs
def cli(directory='.', channels=['conda-forge'], name='my-env'):
    dependencies = parse_pyfiles(directory=directory)
    notebooks = _find_notebooks()
    for notebook in notebooks:
        dependencies.extend(parse_notebook(notebook))
    dependencies = sorted(set(dependencies))

    make_env_file(
        dependencies=dependencies,
        channels=channels,
        name=name,
        )


if __name__ == '__main__':
    cli()
