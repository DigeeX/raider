Definitions
===========

.. glossary::
  .. _definition_hyfiles:
  hyfiles
    The documentation will use the term **hyfiles** to refer to any
    ``*.hy`` file inside the project's configuration directory. Each
    will be evaluated in *alphabetical order* by **Raider**.

    The objects created in previous files are all available in the next
    file, since all the ``locals()`` get preserved and loaded again when
    reading the next file. A common practice is to prepend the file
    names with two digits and an underscore, for example
    ``03_authentication.hy`` and ``09_users.hy``.
  
  .. _definition_authentication:
  Authentication
    The act of proving the identity of a computer system
    user. Authentication in the context of web applications is
    *usually* performed by submitting a username or ID and a piece of
    private information (:term:`factor <Factor>`) such as a
    password. 

    In **Raider** the authentication process is defined by a series of
    :term:`Flow objects <Flow>`.  Those are extracted from the
    ``_authentication`` variable in the :term:`hyfiles <hyfiles>`, and
    stored inside an :class:`raider.authentication.Authentication`
    object. It's also accessible from the :class:`raider.Raider`
    directly:

    .. code-block:: python

         import raider

	 raider = raider.Raider("my_app")
	 raider.authentication


  .. _definition_mfa:
  Multi-factor authentication (MFA)
    An :term:`authentication <Authentication>` method in which the
    user is granted access only after successfully presenting two or
    more pieces of evidence (:term:`factors <Factor>`).

  .. _definition_factor:
  Factor
    A factor can be *something the user knows* (passwords, security
    questions, etc...), *something they have* (bank card, USB security
    key, etc...), *something they are* (fingerprint, eye iris, etc..) or
    *somewhere they are* (GPS location, known WiFi connection, etc...).

  .. _definition_fsm:
  Finite state machine
    A mathematical model of computation abstracting a process that can
    be only in one of a finite number of *states* at any given
    time. Check the `Wikipedia article
    <https://en.wikipedia.org/wiki/Finite-state_machine>`_ for more
    information, since it explains this better than me anyways.

  .. _definition_stage:
  Stage
    A **Raider** concept describing the information exchange between
    the client and server, containing one :term:`request <Request>`
    and the respective response.

  .. _definition_flow:
  Flow
    A **Raider** class implementing :term:`stages <Stage>`. To create
    a :class:`raider.flow.Flow` object, you need to give it a name, a
    Request object, and optionally outputs and :term:`operations
    <Operation>`.  Check the :ref:`Flow configuration page <flows>`
    for more information.

  .. _definition_operation:
  Operation
    A piece of code that will be run after the HTTP response is
    received. All Operations inherit from
    :class:`raider.operations.Operation`.

    All defined Operations inside the :term:`Flow <Flow>` object will
    stop running when the first ``NextStage`` Operation is encountered.

    **Raider** comes with :ref:`some standard operations <operations>`,
    but it also gives the user the flexibility to :ref:`write their own
    Operations easily <operations_api>`.

  .. _definition_functions:
  Functions
    A **Raider** class containing all :term:`Flows <Flow>` objects that
    don't affect the :term:`authentication <Authentication>`
    process. Those are extracted from the :ref:`_functions
    <var_functions>` variable and stored inside an
    :class:`raider.functions.Functions` object.

  .. _definition_plugin:
  Plugin
    A piece of code that can be used to generate inputs for outgoing
    HTTP Requests, and/or extract outputs from incoming Responses. All
    Plugins inherit from :class:`raider.plugins.Plugin`.

    When used inside a :term:`Request <Request>`, Plugins acts as input
    and replace themselves with the actual value.

    When used inside the :term:`Flow's <Flow>` ``:output`` parameter,
    Plugins act as outputs from the HTTP response, and store the
    extracted value for later use.

    **Raider** comes with :ref:`some standard plugins <plugins>`, but it
    also gives the user the flexibility to :ref:`write their own
    Plugins easily <plugin_api>`.


  .. _definition_request:
  Request
    A HTTP request with the defined inputs. In **Raider** it's
    implemented as a separate class
    :class:`raider.request.Request`. This however is not used directly
    most of the times, but as an argument when creating the
    :term:`Flow <Flow>` object in :term:`hyfiles <hyfiles>`.

    When used inside a Request, a :term:`Plugin <Plugin>` will replace
    itself with its actual value during runtime.

  .. _definition_response:
  Response
    A HTTP response from which the outputs are extracted and stored
    inside the :term:`Plugins <Plugin>`.

    When the :term:`Flow <Flow>` object containing this response is
    received and processed, the :term:`Operations <Operation>` are
    executed.
