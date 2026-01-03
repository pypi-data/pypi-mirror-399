
.. image:: https://readthedocs.org/projects/sanhe-atlassian-sdk/badge/?version=latest
    :target: https://sanhe-atlassian-sdk.readthedocs.io/en/latest/
    :alt: Documentation Status

.. image:: https://github.com/MacHu-GWU/sanhe_atlassian_sdk-project/actions/workflows/main.yml/badge.svg
    :target: https://github.com/MacHu-GWU/sanhe_atlassian_sdk-project/actions?query=workflow:CI

.. image:: https://codecov.io/gh/MacHu-GWU/sanhe_atlassian_sdk-project/branch/main/graph/badge.svg
    :target: https://codecov.io/gh/MacHu-GWU/sanhe_atlassian_sdk-project

.. image:: https://img.shields.io/pypi/v/sanhe-atlassian-sdk.svg
    :target: https://pypi.python.org/pypi/sanhe-atlassian-sdk

.. image:: https://img.shields.io/pypi/l/sanhe-atlassian-sdk.svg
    :target: https://pypi.python.org/pypi/sanhe-atlassian-sdk

.. image:: https://img.shields.io/pypi/pyversions/sanhe-atlassian-sdk.svg
    :target: https://pypi.python.org/pypi/sanhe-atlassian-sdk

.. image:: https://img.shields.io/badge/✍️_Release_History!--None.svg?style=social&logo=github
    :target: https://github.com/MacHu-GWU/sanhe_atlassian_sdk-project/blob/main/release-history.rst

.. image:: https://img.shields.io/badge/⭐_Star_me_on_GitHub!--None.svg?style=social&logo=github
    :target: https://github.com/MacHu-GWU/sanhe_atlassian_sdk-project

------

.. image:: https://img.shields.io/badge/Link-API-blue.svg
    :target: https://sanhe-atlassian-sdk.readthedocs.io/en/latest/py-modindex.html

.. image:: https://img.shields.io/badge/Link-Install-blue.svg
    :target: `install`_

.. image:: https://img.shields.io/badge/Link-GitHub-blue.svg
    :target: https://github.com/MacHu-GWU/sanhe_atlassian_sdk-project

.. image:: https://img.shields.io/badge/Link-Submit_Issue-blue.svg
    :target: https://github.com/MacHu-GWU/sanhe_atlassian_sdk-project/issues

.. image:: https://img.shields.io/badge/Link-Request_Feature-blue.svg
    :target: https://github.com/MacHu-GWU/sanhe_atlassian_sdk-project/issues

.. image:: https://img.shields.io/badge/Link-Download-blue.svg
    :target: https://pypi.org/pypi/sanhe-atlassian-sdk#files


Welcome to ``sanhe_atlassian_sdk`` Documentation
==============================================================================
.. image:: https://sanhe-atlassian-sdk.readthedocs.io/en/latest/_static/sanhe_atlassian_sdk-logo.png
    :target: https://sanhe-atlassian-sdk.readthedocs.io/en/latest/

``sanhe_atlassian_sdk`` is a lightweight foundational library for interacting with
`Atlassian REST APIs <https://developer.atlassian.com/cloud/>`_.
It provides a unified HTTP client with both synchronous and asynchronous support,
serving as the base layer for product-specific SDKs.


About
------------------------------------------------------------------------------

This library is designed as a **low-level foundation** that handles common concerns
for Atlassian API interactions:

- **Unified HTTP Client**: Built on `httpx <https://www.python-httpx.org/>`_ for modern,
  high-performance HTTP operations
- **Sync and Async Support**: Seamlessly switch between synchronous and asynchronous
  request patterns based on your application needs
- **Authentication**: Built-in HTTP Basic Authentication for Atlassian Cloud APIs
- **Pydantic Integration**: Uses `Pydantic <https://docs.pydantic.dev/>`_ for robust
  configuration validation

**Product-Specific SDKs**: This library serves as the foundation for higher-level SDKs
that provide product-specific functionality:

- ``sanhe_confluence_sdk`` - Confluence Cloud API operations (coming soon)
- ``sanhe_jira_sdk`` - Jira Cloud API operations (coming soon)


Usage
------------------------------------------------------------------------------

.. code-block:: python

    from sanhe_atlassian_sdk import Atlassian

    # Initialize the client
    client = Atlassian(
        url="https://your-domain.atlassian.net",
        username="your-email@example.com",
        password="your-api-token",  # Use API token, not your account password
    )

    # Use the synchronous client
    response = client.sync_client.get(
        f"{client.url}/wiki/api/v2/spaces",
    )

    # Or use the asynchronous client
    async def fetch_spaces():
        response = await client.async_client.get(
            f"{client.url}/wiki/api/v2/spaces",
        )
        return response.json()

**Note**: For Atlassian Cloud, you should use an
`API token <https://support.atlassian.com/atlassian-account/docs/manage-api-tokens-for-your-atlassian-account/>`_
as the password, not your account password.


.. _install:

Install
------------------------------------------------------------------------------

``sanhe_atlassian_sdk`` is released on PyPI, so all you need is to:

.. code-block:: console

    $ pip install sanhe-atlassian-sdk

To upgrade to latest version:

.. code-block:: console

    $ pip install --upgrade sanhe-atlassian-sdk
