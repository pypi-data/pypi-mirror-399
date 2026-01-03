# python-bap

This project serves as an example on how to **build and publish** a Python package to PyPI.

## Folder structure

The folder structure has been created with [Poetry](https://python-poetry.org/) and it looks like this:

```
python-bap/
  dist/               <- Distributables
  src/
    python_bap/       <- Code for the project
  tests/              <- Tests for the application
.gitignore            <- Patterns to be ignored by git
poetry.lock           <- Dependency lock file
pyproject.toml        <- Config file for the project
README.md             <- This file
```

## Bumping the version

It is possible to bump the version of the project using the `poetry version` command with one of the following values as an argument:

- `patch`
- `minor`
- `major`

## Publishing new version

### Manually

If we want to publish the a version of the project to PyPI manually, we can do that by using the following command:

```bash
poetry publish --build
```

> For this to work, we will need to get a Token from PyPI and configure it so that Poetry uses it to publish the package.

### Using GitHub Actions

In order to get GitHub actions to publish a new version of our code, we will need to do the following:

- In your PyPI account, configure a new [Trusted Publisher](https://pypi.org/manage/project/python-bap/settings/publishing/)
  - Specify Owner
  - Specify repository name
  - Specify the workflow name

Once done, you can create a tag which looks like `cli-vX.X.X` and this will trigger the workflow which will publish the version to PyPI.
