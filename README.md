# What is this

This is a framework designed to test authentication for web
applications. While web proxies like
[ZAProxy](https://www.zaproxy.org/) and
[Burpsuite](https://portswigger.net/burp) allow authenticated tests,
they don't provide features to test the authentication process itself,
i.e. manipulating the relevant input fields to identify broken
authentication. Most authentication bugs in the wild have been found
by manually testing it or writing custom scripts that replicate the
behaviour. **Raider** aims to make testing easier, by providing the
interface to interact with all important elements found in modern
authentication systems.

# Features

**Raider** has the goal to support most of the modern authentication
systems, and here are some features that other tools don't offer:

* Unlimited authentication steps
* Unlimited inputs/outputs for each step
* Ability to conditionally decide the next step
* Running arbitrary operations when receiving the response
* Easy to write custom operations and plugins


# How does it work

**Raider** treats the authentication as a finite state machine. Each
authentication step is a different state, with its own inputs and
outputs. Those can be cookies, headers, CSRF tokens, or other pieces
of information.

Each application needs its own configuration file for **Raider** to
work. The configuration is written in
[Hylang](https://docs.hylang.org/). The language choice was done for
multiple reasons, mainly because it's a Lisp dialect embedded in
Python.

Using Lisp was necessarily since sometimes the authentication can get
quite complex, and using a static configuration file would've not been
enough to cover all the details. Lisp makes it easy to combine code
and data, which is exactly what was needed here.

By using a real programming language as a configuration file gives
**Raider** a lot of power, and with great power comes great
responsibility. Theoretically one can write entire malware inside the
application configuration file, which means you should be careful
what's being executed, and **not to use configuration files from
sources you don't trust**. **Raider** will evaluate everything inside
the .hy files, which means if you're not careful you could shoot
yourself in the foot and break something on your system.

# Installation

**Raider** is available on PyPi:

```
$ pip3 install --user raider
```

# The Documentation is available on [Read the Docs](https://raider.readthedocs.io/en/latest/).
