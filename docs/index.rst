Welcome to Raider's documentation!
==================================

Release v\ |version|.

**Raider** is a tool written to help me test authentication for web applications. While web proxies like ZAProxy and Burpsuite allow you to do authenticated tests, they don't provide features to test the authentication process itself, i.e. manipulating the relevant input fields to identify broken authentication. Most authentication bugs in the wild have been found by manually testing it or writing custom scripts that replicate the behaviour. **Raider** aims to fill this gap by providing the interface to interact with all important elements found in modern authentication systems.

-------------------


User guide
----------

.. toctree::
   :maxdepth: 2
   :caption: Getting started

   user/install
   user/architecture
   user/tutorial
   user/definitions


Configuration
-------------

.. toctree::
   :maxdepth: 2
   :caption: Configuration

   dev/plugins
   dev/operations


API documentation
-----------------

.. toctree::
   :maxdepth: 2
   :caption: API reference

   dev/api


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
