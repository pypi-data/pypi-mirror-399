Client
======

The client module provides HTTP functionality with caching, rate limiting, and retry logic.

.. module:: numistalib.client

NumistaApiClient
----------------

.. autoclass:: NumistaApiClient
   :members:
   :undoc-members:
   :show-inheritance:

NumistaResponse
---------------

.. autoclass:: NumistaResponse
   :members:
   :undoc-members:
   :show-inheritance:
   :no-index:

   Response wrapper that exposes cache status.

   .. attribute:: data
      
      The response payload (dict or list)

   .. attribute:: cached
      
      Boolean indicating if response was served from cache

   .. attribute:: cached_indicator
      
      String emoji: "💾" for cached, "🌐" for fresh

Usage Example
-------------

Basic usage:

.. code-block:: python

   from numistalib.client import NumistaApiClient
   from numistalib.config import Settings

   settings = Settings()

   with NumistaApiClient(settings) as client:
       response = client.get("/types/95420")
       print(f"Cached: {response.cached}")
       print(f"Data: {response.data}")

Async usage:

.. code-block:: python

   import asyncio
   from numistalib.client import NumistaApiClient
   from numistalib.config import Settings

   async def main():
       settings = Settings()
       
       async with NumistaApiClient(settings) as client:
           response = await client.get_async("/types/95420")
           print(f"Data: {response.data}")

   asyncio.run(main())
