import glob
import sys
import textwrap

import depfinder

import easyargs

from git import Repo

from ruamel.yaml import YAML



def binder_url(user, repo):
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


def _get_repo(directory):
    repo = Repo(directory)
    origin = list(repo.remotes.origin.urls)[0]
    origin_url = origin.rsplit('.git', 1)[0]
    if origin_url.startswith('http'):
        return origin_url.rsplit('/', 2)[-2::]
    elif origin_url.startswith('git'):
        return origin_url.rsplit(':')[1].split('/')
    else:
        raise ValueError(f'Could not parse repository for {directory}.')

@easyargs
class NBRR(object):
    def env(self, directory='.', channels=['conda-forge'], name='my-env'):
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
    
    def readme(self, directory='.', summary=None):
        user, repo = _get_repo(directory=directory)
        url = binder_url(user, repo)
        if not summary:
            summary = 'Add your project summary here!'
        return textwrap.dedent(f"""
        # {summary}

        [http://mybinder.org/badge.svg]({url})
        """)


if __name__ == '__main__':
    NBRR()
