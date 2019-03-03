# `nbrr`: Jupyter Notebook Reproducible Repositories

## Continuous Integration Tests

| Platform  | Status                                                                                                                                              |
| --------- | --------------------------------------------------------------------------------------------------------------------------------------------------- |
| Linux     | [![Travis](https://img.shields.io/travis/com/ocefpaf/nbrr/master.svg?label=Linux)](https://travis-ci.com/ocefpaf/nbrr)                              |
| Windows   | [![AppVeyor](https://img.shields.io/appveyor/ci/ocefpaf/nbrr/master.svg?label=Windows)](https://ci.appveyor.com/project/ocefpaf/nbrr/branch/master) |

You create the notebooks, ``nbrr`` will do the rest!

- ``environment.yml`` file for ``conda``:

```shell
nbrr env --notebooks_path . --channel conda-forge --name MyEnv > environment.yml
```

- ``Travis-CI`` and ``AppVeyor`` configurations:

```shell
nbrr travis --notebooks_path . > .travis.yml
```

```shell
nbrr appveyor --notebooks_path . > .appveyor.yml
```

- ``README.md`` with a binder link for your GitHub repository:

```shell
nbrr readme "My Awesome Notebook Collection" --repository . > README.md
```