# What is this

This is a tool I wrote to help me test authentication for web applications. I was not satisfied with the existing tools when I attempted to find bugs in the authentication part of the application. While web proxies like ZAProxy and Burpsuite allow you to do authenticated tests, they don't provide features to test the authentication process itself, i.e. manipulating the relevant input fields to identify broken authentication. Most authentication bugs in the wild have been found by manually testing it or writing custom scripts that replicate the behaviour. Raider aims to make testing easier, by providing the interface to interact with all important elements found in modern authentication systems.

## How does it work

Raider treats the authentication as a finite state machine. Each authentication step is a different state, with its own inputs and outputs. Those can be cookies, headers, CSRF tokens, or other pieces of information.

Each application needs its own configuration file for Raider to work. The configuration is written in [Hylang](https://docs.hylang.org/). The language choice was done for multiple reasons, mainly because it's a Lisp dialect embedded in Python. Using Lisp was necessarily since sometimes the authentication can get quite complex, and using a static configuration file would've not been enough to cover all the details. Lisp makes it easy to combine code and data, which is exactly what I needed here.

By using a real programming language as a configuration file gives Raider a lot of power, and with great power comes great responsibility. Theoretically one can write entire malware inside the application configuration file, which means you should be careful what's being executed, and not to use configuration files from sources you don't trust. Raider will eval everything inside the .hy files, which means if you're not careful you could shoot yourself in the foot and break something on your system.

## Architecture and definitions

Raider treats authentication mechanism like a finite state machine. Each state consists of a single HTTP request with the associated response. This state is called `Flow` in Raider.

### Configuration

Configuration files are located at `~/.config/raider/`. Project specific files are inside the `apps` subdirectory. Each directory inside `apps` represents another project. All *.hy files inside the project directory will be evaluated in alphabetical order. Take at look at [examples](examples/) directory for inspiration. All objects defined in one file will be available inside the next file, which allows to split the configuration however you want.

### Flows

The `Flow` object is used to define the HTTP request with all the inputs, the outputs which will be extracted from the response, operations to do after the stage is finished, and other similar information.

### Outputs

An output is a piece of data we want to extract from the HTTP response. It can be later used as an input to later HTTP requests. For now the following output types are supported:

* Cookie - The cookie from the response will be saved and can later be used as an input.

* Header - Same as Cookie, only the header is saved instead.

* Html - If the piece of information you need is located inside an HTML tag, you can use this object to extract it and pass it down to the next request as input.

* Regex - Same as Html, except it uses regular expressions to extract the information you want.

* Json - Same as Html or Regex, except the information is located inside a JSON body response.


### Inputs

An input is a piece of data that we send with the HTTP request. It can be a cookie, header, or some other information in the HTTP request. They are defined inside the `Request` object. For now Raider supports the following input types:

* Variable - at the moment can be only "username" or "password". Raider will replace the value of the current active user with the correct credential. In the future it will also allow other user relevant data.

* Prompt - Raider will ask for the input value in the command line prompt. This is used for multi-factor authentication code for example.

* Cookie - If a cookie was set up as an output from the previous response it can be passed further as an input to the next request.

* Header - Same as Cookie, except for two header subtypes: ** Basicauth - This header is used for basic authentication.  ** Bearerauth - This is used for bearer authentication with the access token.

* Html - This object will return the value extracted from a previous response. If a HTML tag defined here is found in the request where it's set up as an output, the extracted value will be used as an input when used in a `Request` object.

* Regex - Same as Html, except instead of searching for HTML tags, you search for regular expression inside the response.

* Json - Like Html and Regex, only it returns the information from a JSON response.


### Operations

The `Flow` object accepts the operations parameter, which contains a list of operations that will be performed once the response arrives. These are used to define the relationship between authentication steps, i.e. go to "multi_factor" if the HTTP response code is 302, and finish the authentication if the response code is
200. Once the NextStage operation is encountered, no more operations will be executed, and Raider will move on to the next step of the authentication. For now Raider supports the following operations:

* NextStage - go to the next stage as defined here

* Print - print the value of some extracted output on the command line

* Error - quit Raider with the specified error message

* Grep - this is a conditional operation. The action defined under `:action` will be executed if the regular expression is matched in the HTTP response, and if not, the `:otherwise` operation will be executed.

* Http - this is also a conditional operation. Unlike Grep, it will select which operation to run next based on the HTTP response code.


### Special variables

Raider config files must use several special variables prefixed with underscore for internal purposes. All other variables will only be used inside the config file and not transferred to Raider objects.

* _users - this variable will contain a list of dictionaries with the user credentials. For now only usernames and passwords are evaluated, but in future it will be used for other arbitrary user related information.

  Example:
```
  (setv _users
     [{:username "user1"
	   :password "s3cr3tP4ssWrd1"}
      {:username "user2"
	   :password "s3cr3tP4ssWrd2"}])
```
* _authentication - this variable should contain all of the authentication stages in the `Flow` format. You can define those stages separately as variables like in the tutorial, and include them all at the end in the _authentication variable.

  Example:

```
(setv _authentication
      [initialization
       login
       multi_factor
       get_access_token
       get_unread_messages
       #_ /])
```

* _functions - this variable should contain all of the functions in the `Flow` format. Functions look similar to authentication stages, only they are not considered to affect the authentication process.


* _base_url (optional) - this variable can be used to create shorter request definitions. If set up, you can create `Request` objects with the ":path" parameter instead of the ":url" one, so you don't need the entire URL if it's the same base for all requests.


# Objects

## Modules
* Variable - used as a request input. Accepts one single parameter, the name of the variable. For now only "username" and "password" works. In the future it should be used with arbitrary user relevant data.

  Example: `(setv username (Variable "username"))`

* Prompt - used as a request input. Accepts one single parameter, the prompt to be used when asking for user input on command line.

  Example: `(setv mfa_code (Prompt "MFA:"))`

* Regex - used as both input and output. When used as output, the HTTP response will be checked for the regular expression, and the data from the first group, i.e. the string between `(` and `)` will be saved. When used as input, the extracted string will be returned.

  Example:
  ```
  (setv access_token
      (Regex
        :name "access_token"
        :regex "\"accessToken\":\"([^\"]+)\""))
  ```

  Here, the string between double quotes following `"accessToken":` will be stored and returned when used as input.

* Html - used as both input and output. When used as output, the HTML will be parsed, the specified tag will be selected, and the necessary attribute will be saved. When used as input, this saved value will be returned.

  Example:

  ```
  (setv csrf_token
        (Html
          :name "csrf_token"
          :tag "input"
          :attributes
          {:name "csrf_token"
           :value "^[0-9a-f]{40}$"
           :type "hidden"}
          :extract "value"))

  ```

  Here the `input` tag will be identified, which has the attribute name as `csrf_token`, the type as `hidden` and its value is a 40 character string made out of lowercase hexadecimal digits. The value attribute will be extracted. When used as input, only the extracted string will be returned.

* Json - used as both input and output. When used as output, the JSON body will be parsed, and the specified attribute will be extracted. The `.` (dot) character is used to go deeper inside the JSON object.

  Example:

  ```
  (setv access_token
        (Json
          :name "access_token"
          :extract "body.token"))
  ```

# Running raider

Currently there's no CLI for Raider yet, but this will change. So the
only way to run it now is by writing a small python script using the
Raider library. Once the application is configured, you can
authenticate and call the function `get_nickname` with this script:

```
from raider.raider import Raider

raider = Raider("reddit")
raider.authenticate()
raider.run_function("get_nickname")
```
