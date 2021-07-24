Definitions
===========


.. glossary::
  Authentication
    The act of proving the identity of a computer system
    user. Authentication in the context of web applications is
    *usually* performed by submitting a username or ID and a piece of
    private information (:term:`factor <Factor>`) such as a
    password. 

    In **Raider** the authentication process is defined by a series of
    :term:`Flow objects <Flow>`.  Those are extracted from the
    :ref:`_authentication<var_authentication>` variable in the
    :term:`hyfiles <hyfiles>`, and stored inside an
    :class:`Authentication <raider.authentication.Authentication>`
    object. It's also accessible from the :class:`Raider <raider.Raider>`
    directly:

    .. code-block:: python

         >>> import raider
	 >>> app = raider.Raider("my_app")
	 >>> app.authentication
	 <raider.authentication.Authentication object at 0x7fbf25842dc0>


  Factor
    A factor can be *something the user knows* (passwords, security
    questions, etc...), *something they have* (bank card, USB security
    key, etc...), *something they are* (fingerprint, eye iris, etc..) or
    *somewhere they are* (GPS location, known WiFi connection, etc...).

  Finite state machine
    A mathematical model of computation abstracting a process that can
    be only in one of a finite number of *states* at any given
    time. Check the `Wikipedia article
    <https://en.wikipedia.org/wiki/Finite-state_machine>`_ for more
    information, since it explains this better than me anyways.

  Flow
    A **Raider** class implementing :term:`stages <Stage>`. To create a
    :class:`Flow <raider.flow.Flow>` object, you need to give it a name,
    a :class:`Request <raider.request.Request>` object, and optionally
    outputs and :term:`operations <Operation>`.  Check the :ref:`Flow
    configuration page <flows>` for more information.

  Functions
    A **Raider** class containing all :term:`Flows <Flow>` objects
    that don't affect the :term:`authentication <Authentication>`
    process. The :class:`Functions <raider.functions.Functions>`
    object is extracted from the :ref:`_functions <var_functions>`
    variable.

  hyfiles
    The documentation uses the term **hyfiles** to refer to any
    ``*.hy`` file inside the project's configuration directory. Each
    will be evaluated in *alphabetical order* by **Raider**.

    The objects created in previous files are all available in the next
    file, since all the ``locals()`` get preserved and loaded again when
    reading the next file. A common practice is to prepend the file
    names with two digits and an underscore, for example
    ``03_authentication.hy`` and ``09_users.hy``.
  
  Multi-factor authentication (MFA)
    An :term:`authentication <Authentication>` method in which the
    user is granted access only after successfully presenting two or
    more pieces of evidence (:term:`factors <Factor>`).

  Operation
    A piece of code that will be run after the HTTP :term:`response` is
    received. All Operations inherit from :class:`Operation
    <raider.operations.Operation>` class.

    All defined Operations inside the :term:`Flow <Flow>` object will
    stop running when the first :class:`NextStage
    <raider.operations.NextStage>` Operation is encountered.

    **Raider** comes with :ref:`some standard operations <operations>`,
    but it also gives the user the flexibility to :ref:`write their own
    Operations easily <operations_api>`.

  Plugin

    A piece of code that can be used to generate inputs for outgoing
    HTTP :term:`Requests <Request>`, and/or extract outputs from
    incoming term:`Responses <Response>`. All plugins inherit from
    :class:`Plugin <raider.plugins.Plugin>` class.

    When used inside a :term:`Request <Request>`, Plugins acts as input
    and replace themselves with the actual value.

    When used inside the :term:`Flow's <Flow>` ``:output`` parameter,
    Plugins act as outputs from the HTTP response, and store the
    extracted value for later use.

    **Raider** comes with :ref:`some standard plugins <plugins>`, but it
    also gives the user the flexibility to :ref:`write their own
    Plugins easily <plugin_api>`.

  Project
    To avoid confusion with the :class:`Application
    <raider.application.Application>` class, **Raider** uses the term
    Project to refer to an application, with existing :term:`hyfiles`.

  Request
    A HTTP request with the defined inputs. In **Raider** it's
    implemented as a separate class :class:`Request
    <raider.request.Request>`. This however is not used directly most of
    the times, but as an argument when creating the :term:`Flow <Flow>`
    object in :term:`hyfiles <hyfiles>`.

    When used inside a Request, a :term:`Plugin <Plugin>` will replace
    itself with its actual value during runtime.

  Response
    A HTTP response from which the outputs are extracted and stored
    inside the :term:`Plugins <Plugin>`.

    When the :term:`Flow <Flow>` object containing this response is
    received and processed, the :term:`Operations <Operation>` are
    executed.

  Stage
    A **Raider** concept describing the information exchange between
    the client and server, containing one :term:`request <Request>`
    and the respective response.
