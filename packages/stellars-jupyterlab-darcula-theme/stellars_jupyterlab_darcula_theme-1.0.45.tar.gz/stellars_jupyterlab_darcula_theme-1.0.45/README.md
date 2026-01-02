# Stellars Jupyterlab Darcula Theme

[![GitHub Actions](https://github.com/stellarshenson/jupyterlab_stellars_darcula_theme/actions/workflows/build.yml/badge.svg)](https://github.com/stellarshenson/jupyterlab_stellars_darcula_theme/actions/workflows/build.yml)
[![npm version](https://img.shields.io/npm/v/stellars_jupyterlab_darcula_theme.svg)](https://www.npmjs.com/package/stellars_jupyterlab_darcula_theme)
[![PyPI version](https://img.shields.io/pypi/v/stellars_jupyterlab_darcula_theme.svg)](https://pypi.org/project/stellars_jupyterlab_darcula_theme/)
[![Total PyPI downloads](https://static.pepy.tech/badge/stellars_jupyterlab_darcula_theme)](https://pepy.tech/project/stellars_jupyterlab_darcula_theme)
[![JupyterLab 4](https://img.shields.io/badge/JupyterLab-4-orange.svg)](https://jupyterlab.readthedocs.io/en/stable/)
[![Brought To You By KOLOMOLO](https://img.shields.io/badge/Brought%20To%20You%20By-KOLOMOLO-00ffff?style=flat)](https://kolomolo.com)
[![Donate PayPal](https://img.shields.io/badge/Donate-PayPal-blue?style=flat)](https://www.paypal.com/donate/?hosted_button_id=B4KPBJDLLXTSA)

**IntelliJ Darcula Theme clone tweaked by Stellars**

Yet another Darcula theme clone for jupyterlab, just modernised and tweaked for readability.
This theme has simple, clean colours and minimal intruision into the standard jupyterlab styling.

This project is based on the original [Darcula theme](https://github.com/telamonian/theme-darcula) ported
to the latest [jupyterlab extension template](https://github.com/jupyterlab/extension-template) with copier

![](https://github.com/stellarshenson/jupyterlab_stellars_darcula_theme/blob/master/screenshot-stellars-darcula.png?raw=true)

## Requirements

- JupyterLab >= 4.0.0

## Install

To install the extension, execute:

```bash
pip install stellars_jupyterlab_darcula_theme
```

## Uninstall

To remove the extension, execute:

```bash
pip uninstall stellars_jupyterlab_darcula_theme
```

## Contributing

### Development install

Note: You will need NodeJS to build the extension package.

#### Dependencies

- install nodejs with conda: `conda install nodejs`
- install jupyterlab: `conda install jupyterlab`
- install maketools: `conda install make`
- install build and setuptools: `pip install build setuptools`

#### Build

- invoke `make` to build the `.whl` package
- invoke `make clean` to run cleanup & uninstall
- invoke `make install` to build and install extension
- invoke `make uninstall` to uninstall extension

#### Development

The `jlpm` command is JupyterLab's pinned version of
[yarn](https://yarnpkg.com/) that is installed with JupyterLab. You may use
`yarn` or `npm` in lieu of `jlpm` below.

```bash
# Clone the repo to your local environment
# Change directory to the stellars_jupyterlab_darcula_theme directory
# Install package in development mode
pip install -e "."
# Link your development version of the extension with JupyterLab
jupyter labextension develop . --overwrite
# Rebuild extension Typescript source after making changes
jlpm build
```

You can watch the source directory and run JupyterLab at the same time in different terminals to watch for changes in the extension's source and automatically rebuild the extension.

```bash
# Watch the source directory in one terminal, automatically rebuilding when needed
jlpm watch
# Run JupyterLab in another terminal
jupyter lab
```

With the watch command running, every saved change will immediately be built locally and available in your running JupyterLab. Refresh JupyterLab to load the change in your browser (you may need to wait several seconds for the extension to be rebuilt).

By default, the `jlpm build` command generates the source maps for this extension to make it easier to debug using the browser dev tools. To also generate source maps for the JupyterLab core extensions, you can run the following command:

```bash
jupyter lab build --minimize=False
```

### Development uninstall

```bash
pip uninstall stellars_jupyterlab_darcula_theme
```

In development mode, you will also need to remove the symlink created by `jupyter labextension develop`
command. To find its location, you can run `jupyter labextension list` to figure out where the `labextensions`
folder is located. Then you can remove the symlink named `stellars_jupyterlab_darcula_theme` within that folder.

### Packaging the extension

See [RELEASE](RELEASE.md)
