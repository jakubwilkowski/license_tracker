# License Tracker

Simple utility to fetch and export data about popular python packages.

## Basic usage

The easiest way to use this tool is:
```shell
# build image
docker build . -t license_tracker

# run the tool by providing packages without version or pinned to versions
docker run license_tracker coreapi pytest pyflakes==2.5.0 requests
coreapi (2.3.3) ❗ No licenses found
pytest (7.1.2) ✔
pyflakes (2.5.0) ✔
requests (2.28.1) ✔
Processing... ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 100% 0:00:00
┌────────────────────────────┬───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ Name                       │ pytest                                                                                                                │
│ Version                    │ 7.1.2                                                                                                                 │
│ Summary                    │ pytest: simple powerful testing with Python                                                                           │
│ Project URL                │ https://github.com/pytest-dev/pytest/tree/7.1.2                                                                       │
│ License Name               │ MIT                                                                                                                   │
│ License filename (1)       │ LICENSE                                                                                                               │
│ License download URLs (1)  │ https://raw.githubusercontent.com/pytest-dev/pytest/7.1.2/LICENSE                                                     │
│ License raw contents (1)   │ The MIT License (MIT)
...
```

## Advanced usage

### Accessing docker container

In case of issues with docker containers, they can be entered by overriding
entrypoint, for example:
```shell
docker run -it --entrypoint /bin/bash license_tracker
```

### Setting up locally

`Poetry` is used for dependency management to it needs to be installed in order to run this project

```shell
pip install poetry==1.1.14
poetry install
poetry run python main.py django
```
