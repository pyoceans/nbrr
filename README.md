# `nbrr`: Jupyter Notebook Reproducible Repositories

You create the notebooks, ``nbrr`` will do the rest!

- ``environment.yml`` file for ``conda``:

```shell
nbrr env --directory . --channel conda-forge --name MyEnv --extras "python=3.6,r-base=3.4.2,julia,xlrd,rise" > environment.yml
```

- ``README.md`` with a binder link for your GitHub repository:

```shell
nbrr readme "My Awesome Notebook Collection" --repository . > README.md
```
