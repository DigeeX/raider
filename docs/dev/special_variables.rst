Special variables
=================


.. _var_users:

_users
------

Setting this variable *is required* for **Raider** to run.

It should contain a list of dictionaries with the user credentials. For
now only usernames and passwords are evaluated, but in future it will be
used for other arbitrary user related information. This data gets
converted into a :class:`UserStore <raider.user.UserStore>` object which
provides a dictionary-like structure with :class:`User
<raider.user.User>` objects inside.

Example:

.. code-block:: hylang
		
    (setv _users
       [{:username "user1"
  	 :password "s3cr3tP4ssWrd1"}
        {:username "user2"
         :password "s3cr3tP4ssWrd2"}])   

.. _var_authentication:

_authentication
---------------

This variable *is required* for **Raider** to run.

It should contain all of the authentication stages in Flow
objects. You can define those stages separately as variables like in
the :ref:`tutorial <tutorial>`, and include them all at the end in the
``_authentication`` variable.

Example:

.. code-block:: hylang

    (setv _authentication
          [initialization
           login
           multi_factor
           #_ /])


Where each item in the list is a :class:`Flow <raider.flow.Flow>` object, and
might look like this:

.. code-block:: hylang

    (setv initialization
          (Flow
            :name "initialization"
            :request (Request
                       :method "GET"
                       :path "about")
            :outputs [csrf_token session_id]
            :operations [(Print csrf_token session_id)
                         (Http
                           :status 200
                           :action
                           (NextStage "login")
                           :otherwise
                           (Error "Cannot initialize session"))]))		

.. _var_base_url:

_base_url
---------

This variable *is optional*.

Setting ``base_url`` will enable a shortcut for writing new
:class:`Request <raider.request.Request>` objects. When enabled, the
Requests can be created using ``:path`` instead of ``:url``


.. _var_functions:

_functions
----------

This variable *is optional*.

It works similarly to the :ref:`_authentication <var_authentication>`
variable, but it includes only the Flows which don't affect the
authentication process.
