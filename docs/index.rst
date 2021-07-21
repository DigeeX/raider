Welcome to Raider's documentation!
==================================


**Raider** is a tool designed to test authentication for web
applications. While web proxies like `ZAProxy
<https://www.zaproxy.org/>`_ and `Burpsuite
<https://portswigger.net/burp>`_ allow authenticated tests, they don't
provide features to test the authentication process itself,
i.e. manipulating the relevant input fields to identify broken
authentication. Most authentication bugs in the wild have been found
by manually testing it or writing custom scripts that replicate the
behaviour. **Raider** aims to make testing easier, by providing the
interface to interact with all important elements found in modern
authentication systems.


-------------------


.. toctree::
   :maxdepth: 2
   :caption: Getting started

   user/install
   user/architecture
   user/tutorial
   user/definitions
   user/faq


.. toctree::
   :maxdepth: 2
   :caption: Configuration

   dev/special_variables
   dev/flows
   dev/plugins
   dev/operations


.. toctree::
   :maxdepth: 2
   :caption: API reference

   dev/api


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
