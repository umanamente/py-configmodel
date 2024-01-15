.. These are examples of badges you might want to add to your README:
   please update the URLs accordingly

    .. image:: https://api.cirrus-ci.com/github/<USER>/ConfigModel.svg?branch=main
        :alt: Built Status
        :target: https://cirrus-ci.com/github/<USER>/ConfigModel
    .. image:: https://readthedocs.org/projects/ConfigModel/badge/?version=latest
        :alt: ReadTheDocs
        :target: https://ConfigModel.readthedocs.io/en/stable/
    .. image:: https://img.shields.io/coveralls/github/<USER>/ConfigModel/main.svg
        :alt: Coveralls
        :target: https://coveralls.io/r/<USER>/ConfigModel
    .. image:: https://img.shields.io/pypi/v/ConfigModel.svg
        :alt: PyPI-Server
        :target: https://pypi.org/project/ConfigModel/
    .. image:: https://img.shields.io/conda/vn/conda-forge/ConfigModel.svg
        :alt: Conda-Forge
        :target: https://anaconda.org/conda-forge/ConfigModel
    .. image:: https://pepy.tech/badge/ConfigModel/month
        :alt: Monthly Downloads
        :target: https://pepy.tech/project/ConfigModel
    .. image:: https://img.shields.io/twitter/url/http/shields.io.svg?style=social&label=Twitter
        :alt: Twitter
        :target: https://twitter.com/ConfigModel

.. image:: https://img.shields.io/badge/-PyScaffold-005CA0?logo=pyscaffold
    :alt: Project generated with PyScaffold
    :target: https://pyscaffold.org/


===========
ConfigModel
===========

**ConfigModel** is a Python package that allows you create a config for your
project quickly and easily.



:?: But why should I use **ConfigModel** instead of just using `configparser`?


ConfigModel offers several key advantages over the standard `configparser`:

- **Intellisense bonus**: Your IDE will be able to autocomplete your config parameters, since they are defined as class attributes.

- **Structured Configuration**: Define configurations as nested Python classes, allowing for clear, hierarchical organization.

- **Default Values**: Specify default values within class definitions, ensuring consistency and allowing to generate "distro" configs.

- **Automatic File Generation**: Automatically generate configuration files from class definitions, saving time and reducing manual errors.



Example
=======

Here is a quick example of how to use **ConfigModel**.

First, define a config for your app:

.. code-block:: python

    from configmodel import ConfigModel, config_file, nested_field

    # ============================
    # define a config for your app
    # ============================
    @config_file("config.ini")
    class AppConfig(ConfigModel):
        color_scheme = "dark"
        font_size = 12

        class AccountInfo(ConfigModel):
            username = "guest"
            password = ""
            last_login = ""

        class GoogleApi(ConfigModel):
            client_id = "<put your client id here>"
            secret = "<put your secret here>"

        photos_api = GoogleApi()
        maps_api = GoogleApi()


Then, use your config:

.. code-block:: python

    # ============================
    # use your config
    # ============================
    def main():
        # get config parameter
        print(AppConfig.AccountInfo.username)
        # set config parameters
        AppConfig.AccountInfo.last_login = "2024-01-01"
        AppConfig.photos_api.client_id = "1234"
        AppConfig.maps_api.client_id = "5678"


It will create a config file ``config.ini`` with the following content:

.. code-block:: ini

    [Global]
    color_scheme = dark
    font_size = 12

    [account_info]
    username = guest
    password =
    last_login = 2024-01-01

    [photos_api]
    client_id = 1234
    secret = <put your secret here>

    [maps_api]
    client_id = 5678
    secret = <put your secret here>




Note that

#. You can specify config file name with ``@config_file`` decorator.
#. Section names (``[account_password]``) of nested classes are automatically generated from class names, if no instances of this class are created.
#. You can reuse nested classes (``GoogleApi``) in different places of your config.

