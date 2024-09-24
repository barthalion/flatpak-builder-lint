# flatpak-builder-lint

flatpak-builder-lint is a linter for flatpak-builder manifests, and more widely,
also Flatpak builds. It is primarily developed for Flathub, but can be useful
for other Flatpak repositories.

## Installation

The only supported ways to install and use it are Docker and Flatpak.

### Docker

The latest build of flatpak-builder-linter can be used with Docker.

```
docker run --rm -it ghcr.io/flathub/flatpak-builder-lint:latest
```

You may need to pass the local data using `--volume` to check the chosen file
or repo.

### Flatpak

flatpak-builder-lint is part of the `org.flatpak.Builder` flatpak package
available on Flathub. [Set up Flatpak][flatpak_setup] first, then install
`org.flatpak.Builder`:

```bash
flatpak install flathub -y org.flatpak.Builder
flatpak run --command=flatpak-builder-lint org.flatpak.Builder --help
```

The flatpak package tracks the git commit currently used on the Flathub
infrastructure.

### Local environment

Installing flatpak-builder-lint locally with [Poetry][poetry] or pip is
not recommended unless for development purposes. It depends on patches
that are found in the `org.flatpak.Builder` flatpak package
and on external tools.

For development purposes it can be installed with:

```bash
git clone https://github.com/flathub/flatpak-builder-lint
cd flatpak-builder-lint
poetry install
poetry run flatpak-builder-lint --help
```

After making changes to the code or any dependencies run
`poetry lock --no-update` to regenerate the lockfile (when adding
or changing dependency versions) and `poetry install --sync` to
synchronise the virtual environment.

The following Python dependencies are needed to run
`jsonschema^4.19.1, requests^2.32.2, requests-cache^1.2.1, lxml^5.2.2,
sentry-sdk^2.8.0, PyGObject=^3.48.2`. Additionally `poetry-core>=1.0.0`
is necessary to build.

Additionally the following tools or packages must be installed:

- `libgirepository1.0-dev, gir1.2-ostree-1.0`
- `flatpak-builder` for validating flatpak-builder manifests
- `appstreamcli` from `org.flatpak.Builder` for validating MetaInfo files
```sh
#!/bin/sh

exec flatpak run --branch=stable --command=appstreamcli org.flatpak.Builder ${@}
```
- `desktop-file-validate` to validate desktop files

[Ruff](https://docs.astral.sh/ruff/installation/) is used to lint and
format code. [MyPy](https://mypy.readthedocs.io/en/stable/getting_started.html)
is used to check Python types. To run them:

```sh
# Formatting
poetry run ruff format .

# Linting
poetry run ruff check .

# Auto fix some lint errrors
poetry run ruff check --fix .

# Check python types
poetry run mypy .
```

[Pytest](https://docs.pytest.org/en/stable/getting-started.html) is used
to run tests:

```sh
poetry run pytest -v tests
```

### Usage

```
usage: flatpak-builder-lint [-h] [--version] [--exceptions] [--appid APPID] [--cwd] [--ref REF] {builddir,repo,manifest,appstream} path

A linter for Flatpak builds and flatpak-builder manifests

positional arguments:
  {builddir,repo,manifest,appstream}
                        type of artifact to lint
  path                  path to artifact

options:
  -h, --help            show this help message and exit
  --version             show program's version number and exit
  --exceptions          skip allowed warnings or errors
  --appid APPID         override app ID
  --cwd                 override the path parameter with current working directory
  --ref REF             override the primary ref detection

If you consider the detected issues incorrect, please report it here: https://github.com/flathub/flatpak-builder-lint
```

[poetry]: https://python-poetry.org/docs/#installation
[flatpak_setup]: https://flathub.org/setup

## Documentation

A list of errors and warnings and their explanations are available in the
[Flatpak builder lint page](https://docs.flathub.org/docs/for-app-authors/linter).
