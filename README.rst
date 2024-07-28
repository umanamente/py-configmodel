.. image:: https://img.shields.io/pypi/v/ConfigModel?color=0285f7
   :target: https://pypi.org/project/ConfigModel/
   :alt: PyPI

.. image:: https://readthedocs.org/projects/py-configmodel/badge/?version=latest
   :target: https://py-configmodel.readthedocs.io/en/latest/?badge=latest
   :alt: Documentation

.. image:: https://coveralls.io/repos/github/umanamente/py-configmodel/badge.svg?branch=master
   :target: https://coveralls.io/github/umanamente/py-configmodel?branch=master
    :alt: Coverall

.. image:: https://api.codeclimate.com/v1/badges/1e4b075c05609361d010/test_coverage
   :target: https://codeclimate.com/github/umanamente/py-configmodel/test_coverage
   :alt: Code Climate

.. image:: https://codecov.io/github/umanamente/py-configmodel/graph/badge.svg?token=Z9NU7133FP
   :target: https://codecov.io/github/umanamente/py-configmodel
   :alt: CodeCov

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



Installation
============

You can install **ConfigModel** using ``pip``:

.. code-block:: bash

    pip install ConfigModel

