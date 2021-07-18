Operations
==========

NextStage
---------

Inside the Authentication object NextStage is used to define the
next step of the authentication process. It can also be used inside
"action" attributes of the other Operations to allow conditional
decision making.

.. code-block:: hylang

   (NextStage "login")



Print
-----

When this Operation is executed, it will print each of its elements
in a new line.

.. code-block:: hylang

   (Print
     "This will be printed first"
     access_token
     "This will be printed on the third line")

Error
-----

Operation that will exit Raider and print the error message.

.. code-block:: hylang

   (Error "Login failed.")

Http
----

.. code-block:: hylang

   (Http
      :status 200
      :action
        (NextStage "login")
      :otherwise
        (NextStage "multi_factor"))

Grep
----

.. code-block:: hylang

   (Grep
     :regex "TWO_FA_REQUIRED"
     :action
       (NextStage "multi_factor")
     :otherwise
       (Print "Logged in successfully"))
