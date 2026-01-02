numistalib Documentation
========================

Welcome to **numistalib**, a Python wrapper for the Numista API with built-in caching, rate limiting, and retry logic.

.. toctree::
   :maxdepth: 2
   :caption: User Guide

   installation
   quickstart
   cli_guide
   python_api_guide
   configuration
   advanced_usage

.. toctree::
   :maxdepth: 2
   :caption: API Reference

   api/client
   api/services
   api/models
   api/cli

.. toctree::
   :maxdepth: 1
   :caption: Additional Information

   architecture
   contributing
   CHANGELOG
   license
   DEPLOYMENT
   README

Legal & Attribution
-------------------

This project is an unofficial wrapper and is not affiliated with Numista. When using data from Numista, provide appropriate attribution and comply with Numista’s terms:

- Conditions of use: https://en.numista.com/conditions.php
- Legal information: https://en.numista.com/legal.php
- Pricing API terms: https://en.numista.com/api/pricing.php

Respect Numista’s rate limits and any restrictions on caching or redistribution, particularly for pricing data.

Features
--------

* **Complete API Coverage**: Access all Numista API endpoints
* **HTTP Caching**: RFC 9111-compliant persistent caching with hishel (7-day TTL)
* **Rate Limiting**: Configurable throttling (45 requests/minute default)
* **Retry Logic**: Exponential backoff with jitter for resilient requests
* **Rich CLI**: Beautiful command-line interface with tables and colors
* **Type Safety**: Full Pydantic models with strict validation
* **Sync/Async Support**: Both synchronous and asynchronous client implementations

Quick Example
-------------

CLI Usage
~~~~~~~~~

.. code-block:: bash

   # Search for coins
   numistalib types search -q "dollar"
   
   # Get detailed information
   numistalib types get 95420
   
   # List all catalogues
   numistalib catalogues

Python API Usage
~~~~~~~~~~~~~~~~

.. code-block:: python

   from numistalib.client import NumistaApiClient
   from numistalib.config import Settings
   from numistalib.services.types.service import TypeService
   
   settings = Settings()
   
   with NumistaApiClient(settings) as client:
       service = TypeService(client)
       
       # Search for types
       results = service.search_types(query="dollar", page=1, count=10)
       for coin_type in results:
           print(f"{coin_type.numista_id}: {coin_type.title}")

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
