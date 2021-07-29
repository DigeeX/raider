.. _tutorial:

Tutorial
========

Preparation
-----------

Before you can use **Raider**, you have to set up the
:term:`authentication` inside :term:`hyfiles`. To do that, you'll
probably need to use a web proxy (`BurpSuite
<https://portswigger.net/burp>`_, `ZAProxy
<https://www.zaproxy.org/>`_, `mitmproxy <https://mitmproxy.org/>`_,
etc...)  to see the :term:`requests <Request>` the application is
generating, and identify all the important inputs and outputs for each
request.

After the traffic was captured, there will probably be lots of HTTP
requests that are irrelevant to the authentication. Start by removing
all static files (.png, .js, .pdf, etc...). When you're left with a
fewer requests to deal with, it's time to dive deeper and understand
how the authentication works.

At this point we assume *you already know* the basics of Python and
Hylang so this documentation will not cover information that can be
found somewhere else.

This tutorial will show the authentication in use by Reddit at the
time of writing this. It could be different in the future when you're
reading this, if they update the way authentication works or change
the HTML structure, so you will have to do this all by yourself
anyways.

The easiest way to start this is by going backwards starting with one
authenticated request. This should be some kind of request that only
works when the user is already authenticated. I choose the
"unread_message_count" one for reddit, and the request looks like
this:
       
.. code-block:: 

       GET https://s.reddit.com/api/v1/sendbird/unread_message_count HTTP/1.1
       User-Agent: Mozilla/5.0 (X11; Linux x86_64; rv:89.0) Gecko/20100101 Firefox/89.0
       Accept: application/json
       Accept-Language: en-US,en;q=0.5
       Content-Type: application/json
       Origin: https://www.reddit.com
       DNT: 1
       Authorization: Bearer [REDACTED TOKEN]
       Referer: https://www.reddit.com/
       Connection: keep-alive
       Host: s.reddit.com

       
As you can see from this, the only information we sent to this URL
from our authentication is the Bearer token.
       
We define a new :term:`Flow` that will check for the unread messages
in hy:
       
.. code-block:: hylang

       (setv get_unread_messages
             (Flow
               :name "get_unread_messages"
               :request (Request
                          :method "GET"
                          :headers [(Header.bearerauth access_token)]
                          :url "https://s.reddit.com/api/v1/sendbird/unread_message_count")))

       
In Hy, ``setv`` is used to set up new variables. Here we created the
variable ``get_unread_messages`` that will hold the information about
this Flow. This will be hold in the :ref:`_functions special variable
<var_functions>` which stores the Flows which aren't affecting the
authentication.
       
The only required parameters for :class:`Flow <raider.flow.Flow>`
objects are the name and the request. The name is a string that is used
for reference purposes, and the request contains the actual HTTP request
definition as a :class:`Request <raider.request.Request>` object.
       
The Request object requires only the method and url. Other parameters
are optional. We translate the original request into **Raider** config
format, and to use the access token we need to define it in the request
header. Since this is a bearer header, we use :class:`Header.bearerauth
<raider.plugins.Header>` with the ``access_token`` which we will create
later on.
       
       
Getting the access token
------------------------
       
The next step would be to find out where is this token generated and
how we can extract it. Searching for this token in previous responses,
we can see it was first seen in a request to the main reddit
page. It's located inside the `<script id="data">` part of the
response, and it looks like this:
       
.. code-block::

       [...] "session":{"accessToken":"[REDACTED_TOKEN]","expires":"2021-06-23T19:30:10.000Z" [...]


The easiest way to extract the token using **Raider**, is to use the
:ref:`Regex <plugin_regex>` module. This module searches for the regex
you supplied and returns the value of the first group that
matches. The group is the string in between ``(`` and ``)``
characters. The final object I configured looks like this:
       
.. code-block:: hylang

       (setv access_token
             (Regex
               :name "access_token"
               :regex "\"accessToken\":\"([^\"]+)\""))
       
We are setting up the variable ``access_token`` to the ``Regex`` object,
with the internal name ``access_token`` and that'll return the value of
the string between double quotes after the "accessToken" part.
       
Now we need to define the actual request that will get us this access
token. To do this, we take a closer look to the actual request where
this response was created:
       
.. code-block::
   
       GET https://www.reddit.com/ HTTP/1.1
       User-Agent: Mozilla/5.0 (X11; Linux x86_64; rv:89.0) Gecko/20100101 Firefox/89.0
       Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8
       Accept-Language: en-US,en;q=0.5
       DNT: 1
       Upgrade-Insecure-Requests: 1
       Connection: keep-alive
       Cookie: csv=1; edgebucket=PPJTEvVRvoolrqFkYw; G_ENABLED_IDPS=google; loid=[REDACTED]; eu_cookie={%22opted%22:true%2C%22nonessential%22:false}; token_v2=[REDACTED]; reddit_session=[REDACTED]
       Host: www.reddit.com

       
Now we can see there are several cookies being sent with this
request. Most of them are irellevant here. To see which one is
required for the request to succeed, we remove them one by one and see
if we get the information we need inside the response. By doing this,
I found out that the only cookie we need is ``reddit_session``. As
long as we supply it in the request, we do get the ``access_token`` in
the response. With this information, we can now write the definition
of the request:
       
       
.. code-block:: hylang

       (setv get_access_token
             (Flow
               :name "get_access_token"
               :request (Request
                          :method "GET"
                          :url "https://www.reddit.com/"
                          :cookies [reddit_session])
               :outputs [access_token]
               :operations [(Print access_token)
                            (NextStage "get_unread_messages")]))

       
Here we can see that we specified the ``reddit_session`` cookie to be
sent with the request, and ``access_token`` as the only output generated
from the response.
       
Now we define the cookie like this:
       
.. code-block:: hylang

       (setv reddit_session (Cookie "reddit_session"))

       
When the stage is complete, two operations will be executed. The first
will print the value of the ``access_token`` on the command line, and
the next will tell **Raider** to go to the next stage that we defined
previously.
       

Multi-factor authentication
---------------------------

To show how **Raider** works with multi-factor authentication, I have
enabled it on my reddit account, and added this step to the
configuration. In the web proxy, the request looks like this:
       
.. code-block::
   
       POST https://www.reddit.com/login HTTP/1.1
       User-agent: digeex_raider/0.0.1
       Accept: */*
       Connection: keep-alive
       Cookie: session=[REDACTED]
       Content-Length: 154
       Content-Type: application/x-www-form-urlencoded
       Host: www.reddit.com
       
       password=[REDACTED]&username=[REDACTED]&csrf_token=[REDACTED]&otp=566262&dest=https%3A%2F%2Fwww.reddit.com

       
Now we translate the request in the **Raider** Request type:
       
.. code-block:: hylang
   
       (Request
          :method "POST"
          :url "https://www.reddit.com/login"
          :cookies [session_id]
          :data
          {"password" password
           "username" username
           "csrf_token" csrf_token
           "otp" mfa_code
           "dest" "https://www.reddit.com"})

       
Here we use the new cookie called ``session_id`` that we define as:
       
.. code-block:: hylang

       (setv session_id (Cookie "session"))

       
To use the username and password of the active user, we create two new
inputs of type :ref:`Variable <plugin_variable>`:
       
.. code-block:: hylang
   
       (setv username (Variable "username"))
       (setv password (Variable "password"))

The nickname can be extracted with a Regex:

.. code-block:: hylang

  (setv nickname
      (Regex
        :name "nickname"
        :regex "href=\"/user/([^\"]+)"))
		
       
The multi-factor authentication code will be given as an input to the
CLI manually, so we define the ``mfa_code`` as a :ref:`Prompt
<plugin_prompt>` plugin:
       
.. code-block:: hylang

       (setv mfa_code (Prompt "MFA"))

       
The ``csrf_token`` value will be defined later on.
       
I defined the multi_factor stage as shown below:
       
.. code-block:: hylang
   
       (setv multi_factor
             (Flow
               :name "multi_factor"
               :request (Request
                          :method "POST"
                          :url "https://www.reddit.com/login"
                          :cookies [session_id]
                          :data
                          {"password" password
                           "username" username
                           "csrf_token" csrf_token
                           "otp" mfa_code
                           "dest" "https://www.reddit.com"})
               :outputs [reddit_session]
               :operations [(Print reddit_session csrf_token)
                            (Http
                              :status 200
                              :action
                              (NextStage "get_access_token"))
                            (Http
                              :status 400
                              :action
                              (Grep
                                :regex "WRONG_OTP"
                                :action
                                (NextStage "initialization")
                                :otherwise
                                (Error "Multi-factor authentication error")))]))

       
The only useful output that this stage will generate is the
``reddit_session`` cookie.
       
Now looking at the operations, several things are happening here. The
first operations will just print to the CLI output the values of the
``csrf_token`` and ``reddit_session``.

The second operation will instruct **Raider** to go to the
``get_access_token`` stage if the HTTP response code is 200.

The third operation will run only if the status code is 400, which
means the authentication failed. Inside the response body of a failed
request will be a message indicating why it failed. **Raider** will
then :ref:`Grep <operations_grep>` the response for the string
"WRONG_OTP" in case we gave the wrong multi-factor authentication
code. If it matches, **Raider** will go to the ``initialization``
stage starting the authentication from a clean state again.

We will define this stage later in this tutorial. If the string
"WRONG_OTP" isn't found, **Raider** will quit with the error message
"Multi-factor authentication error".
       

Login
-----
       
On reddit, the login request looks similar to the multi-factor one, so
the stage definition is pretty similar:
       
.. code-block:: hylang

       (setv login
             (Flow
               :name "login"
               :request (Request
                          :method "POST"
                          :url "https://www.reddit.com/login"
                          :cookies [session_id]
                          :data
                          {"password" password
                           "username" username
                           "csrf_token" csrf_token
                           "otp" ""
                           "dest" "https://www.reddit.com"})
               :outputs [session_id reddit_session]
               :operations [(Print session_id reddit_session)
                            (Http
                              :status 200
                              :action
                              (Grep
                                :regex "TWO_FA_REQUIRED"
                                :action
                                (NextStage "multi_factor")
                                :otherwise
                                (NextStage "get_access_token"))
                              :otherwise
                              (Error "Login error"))]))
       
Getting the CSRF token
----------------------
       
Only piece of information we're missing at this point is the CSRF
token.
       
And now, for the ``csrf_token`` we need to find out where it was
created. Searching inside the web proxy for the value of the token, we
find it in a previous response. The relevant part of the HTML code
looks like this:
       
.. code-block::
		
       <input type="hidden" name="csrf_token" value="8309984e972e6608475765db68e25ffb8c0bedc9">

       
So we have its value inside the ``input`` tag, of type ``hidden``, with
the name ``csrf_token``. The actual value is a 40 character string made
out of lowercase hexadecimal characters. We define this as a :ref:`Html
<plugin_html>` plugin:
       
.. code-block:: hylang

       (setv csrf_token
             (Html
               :name "csrf_token"
               :tag "input"
               :attributes
               {:name "csrf_token"
                :value "^[0-9a-f]{40}$"
                :type "hidden"}
               :extract "value"))

       
This object will extract the ``csrf_token`` value, and use it as an
input where necessary.
       
The token can be found by multiple means. The simplest way I found is
by sending a simple GET request to https://www.reddit.com/login/ with
no additional information. Now we can define this stage:
       
.. code-block:: hylang
       
       (setv initialization
             (Flow
               :name "initialization"
               :request (Request
                          :method "GET"
                          :url "https://www.reddit.com/login/")
               :outputs [csrf_token session_id]
               :operations [(Print session_id csrf_token)
                            (NextStage "login")]))

       
Finishing configuration
-----------------------

The request will give us the token we need, and the session
cookie. The configuration file is almost complete. To finish, we set
the special variables:

* :ref:`_authentication <var_authentication>` - containing the list of
  the authentication steps we defined.
  
* :ref:`_functions <var_functions>` - we will put the other defined
  Flows which don't affect authentication.
       
* :ref:`_users <var_users>` - user credentials go here


Adding one more function `get_nickname`, and the complete
configuration file for reddit looks like this:
       

.. code-block:: hylang

   (print "Reddit")
   (setv _base_url "https://www.reddit.com/")
          
   (setv username (Variable "username"))
   (setv password (Variable "password"))
   (setv mfa_code (Prompt "MFA"))
          
   (setv csrf_token
     (Html
       :name "csrf_token"
       :tag "input"
       :attributes
       {:name "csrf_token"
        :value "^[0-9a-f]{40}$"
        :type "hidden"}
       :extract "value"))
          
   (setv access_token
     (Regex
        :name "access_token"
   	:regex "\"accessToken\":\"([^\"]+)\""))
          
   (setv session_id (Cookie "session"))
   (setv reddit_session (Cookie "reddit_session"))
          
          
   (setv initialization
     (Flow
       :name "initialization"
       :request (Request
                 :method "GET"
       		 :url "https://www.reddit.com/login/")
       :outputs [csrf_token session_id]
       :operations
       [(Print session_id csrf_token)
        (NextStage "login")]))
          
   (setv login
     (Flow
       :name "login"
       :request (Request
               :method "POST"
     	       :url "https://www.reddit.com/login"
     	       :cookies [session_id]
     	       :data
     	       {"password" password
     	        "username" username
     		"csrf_token" csrf_token
     		"otp" ""
     		"dest" "https://www.reddit.com"})
      :outputs [session_id reddit_session]
      :operations
      [(Print session_id reddit_session)
       (Http
        :status 200
        :action
         (Grep
          :regex "TWO_FA_REQUIRED"
     	:action
     	 [(Print "Multi-factor authentication required")
     	  (NextStage "multi_factor")]
     	:otherwise (NextStage "get_access_token"))
        :otherwise (Error "Login error"))]))
          
   (setv multi_factor
     (Flow
      :name "multi_factor"
      :request (Request
                 :method "POST"
                 :url "https://www.reddit.com/login"
                 :cookies [session_id]
                 :data
                 {"password" password
                  "username" username
                  "csrf_token" csrf_token
                  "otp" mfa_code
                  "dest" "https://www.reddit.com"})
      :outputs [reddit_session]
      :operations [(Print reddit_session)
                   (Print csrf_token)
                   (Http
                     :status 200
                     :action
                     (NextStage "get_access_token"))
                   (Http
                     :status 400
                     :action
                     (Grep
                       :regex "WRONG_OTP"
                       :action
                       (NextStage "initialization")
                       :otherwise
                       (Error "Multi-factor authentication error")))]))
   
   
   (setv get_access_token
     (Flow
       :name "get_access_token"
       :request (Request
                  :method "GET"
                  :url "https://www.reddit.com/"
                  :cookies [reddit_session])
       :outputs [access_token]
       :operations [(Print access_token)
                    (NextStage "get_unread_messages")]))
   
   (setv get_unread_messages
     (Flow
       :name "get_unread_messages"
       :request (Request
                  :method "GET"
                  :headers [(Header.bearerauth access_token)]
                  :url "https://s.reddit.com/api/v1/sendbird/unread_message_count")))
   
   (setv nickname
         (Regex
           :name "nickname"
           :regex "href=\"/user/([^\"]+)"))

   (setv get_nickname
         (Flow
           :name "get_nickname"
           :request (Request
                      :method "GET"
                      :cookies [session_id reddit_session]
                      :path "/")
           :outputs [nickname]
           :operations [(Print nickname)]))


   (setv _authentication
     [initialization
      login
      multi_factor
      get_access_token])


   (setv _functions
     [get_unread_messages
      get_nickname])


   (setv _users
      [{:username "user1"
        :password "s3cr3tP4ssWrd1"}])



Running Raider
--------------


Now, with the configuration finished, we can run **Raider** with a python
script:

.. code-block:: python

   import raider
   
   app = raider.Raider("reddit")
   # Create a Raider() object for application "reddit"
   
   app.config.proxy = "http://localhost:8080"
   # Run traffic through the local web proxy

   app.authenticate()
   # Run authentication stages one by one
   
   app.run_function("get_nickname")
   app.run_function("get_unread_messages")
   # Run both defined functions


Running the script, we can see its output, and entries in the web
proxy listening on port 8080:

.. code-block::

   $ python script.py

   Reddit
   INFO:root:Running stage initialization
   session = [REDACTED]
   csrf_token = [REDACTED]
   INFO:root:Running stage login
   WARNING:root:Couldn't extract output: session
   WARNING:root:Couldn't extract output: reddit_session
   session = [REDACTED]
   reddit_session = None
   Multi-factor authentication enabled
   INFO:root:Running stage multi_factor
   reddit_session = [REDACTED]
   csrf_token = [REDACTED]
   INFO:root:Running stage get_access_token
   access_token = [REDACTED]
   INFO:root:Running function get_nickname
   nickname = [REDACTED]


   
