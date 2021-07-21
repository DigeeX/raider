.. _plugins:
.. module:: raider.plugins

Plugins
=======

Variable
--------

.. autoclass:: Variable

Prompt
------

.. autoclass:: Prompt

Cookie
------

.. autoclass:: Cookie
	       
Header
------

.. autoclass:: Header

Regex
-----

.. autoclass:: Regex
	       
Html
----

.. autoclass:: Html
	       
Json
----

.. autoclass:: Json

.. _plugin_api:


Plugin API
----------

.. autoclass:: Plugin


Writing custom plugins
----------------------


In case the existing plugins are not enough, the user can write
their own to add the new functionality. Those new plugins should be
written in the project's configuration directory in a ".hy" file. To
do this, a new class has to be defined, which will inherit from
*Raider*'s Plugin class:


Let's assume we want a new plugin that will use `unix password store
<https://www.passwordstore.org/>`_ to extract the OTP from our website.


.. code-block:: hylang


    (defclass PasswordStore [Plugin]
    ;; Define class PasswordStore which inherits from Plugin

      (defn __init__ [self path]
      ;; Initiatialize the object given the path

        (.__init__ (super)
                   :name path
                   :function (. self run_command)))
      ;; Call the super() class, i.e. Plugin, and give it the
      ;; path as the name identifier, and the function
      ;; self.run_command() as a function to get the value.
      ;;
      ;; We don't need the response nor the user data to use
      ;; this plugin, so no flags will be set.
		   
      (defn run_command [self]
        (import os)
	;; We need os.popen() to run the command
	
        (setv self.value
              ((. ((. (os.popen
                        (+ "pass otp " self.path))
                      read))
                  strip)))
	;; set self.value to the output from "pass otp",
	;; with the newline stripped.
	
        (return self.value)))


And we can create a new variable that will use this class:

.. code-block:: hylang

    (setv mfa_code (PasswordStore "personal/reddit"))


Now whenever we use the ``mfa_code`` in our requests, its value will
be extracted from the password store.
