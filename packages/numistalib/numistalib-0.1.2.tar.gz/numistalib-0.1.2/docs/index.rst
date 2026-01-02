numistalib Documentation
========================

A Python caching API wrapper for the Numista numismatic database with RFC 9111-compliant HTTP caching, intelligent rate limiting, and resilient retry logic.

**Includes an optional command-line interface with rich terminal output and sixel image support.**

.. image:: https://github.com/wells01440/numistalib/actions/workflows/test.yml/badge.svg
   :target: https://github.com/wells01440/numistalib/actions/workflows/test.yml
   :alt: Tests

.. image:: https://readthedocs.org/projects/numistalib/badge/?version=latest
   :target: https://numistalib.readthedocs.io/en/latest/?badge=latest
   :alt: Documentation Status

.. image:: https://img.shields.io/pypi/v/numistalib
   :target: https://pypi.org/project/numistalib/
   :alt: PyPI

.. image:: https://img.shields.io/badge/License-MIT-yellow.svg
   :target: https://opensource.org/licenses/MIT
   :alt: License

Features
--------

**Core API Features**

* **RFC 9111-Compliant HTTP Caching**: Persistent SQLite cache with configurable TTL and LRU eviction
* **Intelligent Rate Limiting**: Transport-level throttling with configurable limits (respects Numista quotas)
* **Resilient Retry Logic**: Exponential backoff with jitter for network failures and rate limit errors
* **Complete Type Safety**: Full Pydantic v2 models with strict validation for all API entities
* **Sync & Async Support**: Both synchronous and asynchronous client implementations
* **Cache Indicators**: Visual feedback (💾/🌐) for cache hits/misses in responses

**Optional CLI Features**

* **Rich Terminal UI**: Beautiful tables, panels, and formatted output
* **Sixel Image Support**: Display coin images directly in terminal (Kitty, WezTerm, iTerm2, mlterm, foot, yaft)
* **Flexible Display Modes**: Table or panel mode for different output preferences
* **Command Aliases**: Short and long form commands

Getting Started
---------------

See the following sections to get started:

.. toctree::
   :maxdepth: 2
   :caption: User Guide

   installation
   quickstart
   python_api_guide
   cli_guide
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

About
-----

**Built With**

This project leverages excellent open-source libraries:

* `httpx <https://www.python-httpx.org/>`_ — Modern HTTP client with sync/async support
* `hishel <https://hishel.com/>`_ — RFC 9111-compliant HTTP caching
* `pydantic <https://docs.pydantic.dev/>`_ — Data validation and settings management
* `pyrate-limiter <https://github.com/vutran1710/PyrateLimiter>`_ — Sophisticated rate limiting
* `tenacity <https://tenacity.readthedocs.io/>`_ — Retry logic with exponential backoff
* `click <https://click.palletsprojects.com/>`_ — CLI framework
* `rich <https://rich.readthedocs.io/>`_ — Terminal UI and formatting
* `textual-image <https://github.com/Textualize/textual-image>`_ — Sixel protocol image display

**Legal & Attribution**

This project is an unofficial wrapper and is not affiliated with Numista. When using data from Numista, provide appropriate attribution and comply with Numista's terms:

* `Conditions of use <https://en.numista.com/conditions.php>`_
* `Legal information <https://en.numista.com/legal.php>`_
* `Pricing API terms <https://en.numista.com/api/pricing.php>`_

Respect Numista's rate limits and any restrictions on caching or redistribution, particularly for pricing data.

Indices and Tables
------------------

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
