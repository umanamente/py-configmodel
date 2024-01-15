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


Contents
========

.. toctree::
   :maxdepth: 2

   Overview <readme>
   Contributions & Help <contributing>
   License <license>
   Authors <authors>
   Changelog <changelog>
   Module Reference <api/modules>


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

.. _toctree: https://www.sphinx-doc.org/en/master/usage/restructuredtext/directives.html
.. _reStructuredText: https://www.sphinx-doc.org/en/master/usage/restructuredtext/basics.html
.. _references: https://www.sphinx-doc.org/en/stable/markup/inline.html
.. _Python domain syntax: https://www.sphinx-doc.org/en/master/usage/restructuredtext/domains.html#the-python-domain
.. _Sphinx: https://www.sphinx-doc.org/
.. _Python: https://docs.python.org/
.. _Numpy: https://numpy.org/doc/stable
.. _SciPy: https://docs.scipy.org/doc/scipy/reference/
.. _matplotlib: https://matplotlib.org/contents.html#
.. _Pandas: https://pandas.pydata.org/pandas-docs/stable
.. _Scikit-Learn: https://scikit-learn.org/stable
.. _autodoc: https://www.sphinx-doc.org/en/master/ext/autodoc.html
.. _Google style: https://google.github.io/styleguide/pyguide.html#38-comments-and-docstrings
.. _NumPy style: https://numpydoc.readthedocs.io/en/latest/format.html
.. _classical style: https://www.sphinx-doc.org/en/master/domains.html#info-field-lists
