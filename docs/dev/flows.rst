.. _flows:

Flows
=====

:term:`Flows <Flow>` are the main concept in **Raider**, used to
define the HTTP information exchange. Each :term:`request` you want to
send needs its own Flow object. Inside the ``request`` attribute of
the object, needs to be a :class:`Request <raider.request.Request>`
object containing the definition of the request. This definition can
contain :class:`Plugins <raider.plugins.Plugin>` whose value will be
used when sending the HTTP request.

.. automodule:: raider.flow
   :members:


Examples
--------

Create the variable ``initialization`` with the Flow. It'll send a
request to the :ref:`_base_url <var_base_url>` using the path
``admin/``. If the HTTP response code is 200 go to next stage
``login``.

.. code-block:: hylang

    (setv initialization
          (Flow
            :name "initialization"
            :request (Request
                       :method "GET"
                       :path "admin/")
            :operations [(Http
                           :status 200
                           :action (NextStage "login"))]))
    

Define Flow ``login``. It will send a POST request to
``https://www.example.com/admin/login`` with the username and the
password in the body. Extract the cookie ``PHPSESSID`` and store it in
the ``session_id`` plugin. If server responds with HTTP 200 OK, print
``login successfully``, otherwise quit with the error message ``login
error``.

.. code-block:: hylang

    (setv username (Variable "username"))
    (setv password (Variable "password"))
    (setv session_id (Cookie "PHPSESSID"))

    (setv login
          (Flow
            :name "login"
            :request (Request
                       :method "POST"
                       :url "https://www.example.com/admin/login"
                       :data
                       {"password" password
                        "username" username})
            :outputs [session_id]
            :operations [(Http
                           :status 200
                           :action (Print "login successfully")
                           :otherwise (Error "login error"))]))
    		


Define another ``login`` Flow. Here what's different is the
``csrf_name`` and ``csrf_value`` plugins. In this application both the
name and the value of the token needs to be extracted, since they change
all the time. They were defined as :class:`Html <raider.plugins.Html>`
objects. Later they're being used in the body of the :class:`Request
<raider.request.Request>`.

If the HTTP response code is 200 means the :term:`MFA <Multi-factor
authentication (MFA)>` was enabled and the ``multi_factor`` :term:`stage`
needs to run next. Otherwise, try to log in again. Here the password
is asked from the user by a :class:`Prompt <raider.plugins.Prompt>`.

.. code-block:: hylang

    (setv username (Variable "username"))
    (setv password (Prompt "password"))
    (setv session_id (Cookie "PHPSESSID"))
    
    (setv csrf_name
          (Html
            :name "csrf_name"
            :tag "input"
            :attributes
            {:name "^[0-9A-Fa-f]{10}$"
             :value "^[0-9A-Fa-f]{64}$"
             :type "hidden"}
            :extract "name"))
    
    (setv csrf_value
          (Html
            :name "csrf_value"
            :tag "input"
            :attributes
            {:name "^[0-9A-Fa-f]{10}$"
             :value "^[0-9A-Fa-f]{64}$"
             :type "hidden"}
            :extract "value"))


    (setv login
          (Flow
            :name "login"
            :request (Request
                       :method "POST"
                       :path "/login.php"
                       :cookies [session_id]
                       :data
                       {"open" "login"
                        "action" "customerlogin"
                        "password" password
                        "username" username
                        "redirect" "myaccount"
                        csrf_name csrf_value})
            :outputs [csrf_name csrf_value]
            :operations [(Http
                           :status 200
                           :action (NextStage "multi_factor")
                           :otherwise (NextStage "login"))]))
		
