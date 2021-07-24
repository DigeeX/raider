.. _architecture:

Architecture
============


Abstracting the authentication process
--------------------------------------

First let's start by taking a closer look at how web authentication
works. Every :term:`authentication process <authentication>` can be
abstracted as a :term:`Finite State Machine <Finite state machine>`.

On a high level, we start in the unauthenticated state, the user sends
the application their credentials, optionally the :term:`multi-factor
authentication (MFA)` code, and if both checks pass, we reach the
authenticated state. A typical modern web application will looks like
the following in a diagram:

.. uml:: ../diagrams/high_level_authentication.uml


Basic concepts in Raider
------------------------

Now let's zoom in and look at the details. Instead of dealing with the
states (*Unauthenticated*, *Login failed*, *MFA required*, and
*Authenticated*), we define the concept of :term:`stages
<stage>`, which describes the information exchange between
the client and the server containing one request and the respective
response.

The example below shows a closer look of the authentication process
for an imaginary web application:

.. uml:: ../diagrams/detailed_authentication.uml


To describe the authentication process from the example defined above,
we need three **stages**. The first one, *Initialization*, doesn't
have any inputs, but creates the *Session cookie* and the *CSRF token*
as outputs.

Those outputs are passed to the next **stage**, *Login*, together with
user credentials. A request is built with those pieces of information,
and the new outputs are generated. In this case we have the new *CSRF
token*, an updated *session cookie*, and a new cookie identifying the
user: *user cookie*.

Depending on whether MFA is enabled or not, the third **stage**
*Multi-factor authentication* might be skipped or executed. If it's
enabled, the outputs from the previous **stage** get passed as inputs
to this one, the user is asked to input the next :term:`Factor`, and a
new cookie is set proving the user has passed the checks and is
properly authenticated.

In **Raider**, stages are implemented using :term:`Flow
<Flow>` objects. The authentication process consists of a
series of Flows connected to each other. Each one accepts inputs and
generates outputs. In addition to that, Flow objects implement
:term:`Operations <operation>` which can be used to run
various actions upon receiving the response, but most importantly
they're used to control the authentication process by conditionally or
unconditionally defining the next stage. So for example one can jump
to stage X if the HTTP response code is 200 or to stage Y if it's 403.


.. uml:: ../diagrams/raider_flows.uml


Inputs and outputs are often the same object, and you may want to
update its value from one Flow to the next (for example the CSRF token
changes for every stage). This was implemented in Raider using
:term:`Plugins <Plugin>`.

Plugins are pieces of code that can act as inputs for the HTTP requests
to be sent, and/or as outputs from the HTTP responses. They are used to
facilitate the information exchange between Flows. **Raider** provides
the user the option to :ref:`write new plugins <plugin_api>` with a
small piece of hylang code.


Once the response is received, the :term:`Operations <operation>` will
be executed. The primary function of operations is to define which Flow
comes next. But they can do anything, and *Raider* :ref:`makes it easy
to write new operations <operations_api>`.
