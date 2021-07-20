Installing Raider
=================

The package is available in the `Python Package Index
<https://pypi.org/>`_, so to install the latest stable release of
*Raider* just use the command ``pip3 install --user raider``

.. WARNING:: *Raider* was developed on Python 3.9 and it wasn't tested
             yet on older versions, so it might have incompatibility
             issues.

If you feel adventurous and want to build *Raider* from source, you
can do so. You will need to do that anyways if you want to contribute
to the development.

First start by clonning the repository with ``git clone
https://github.com/DigeeX/raider``.

Using a python virtual environment is recommended to avoid weird
issues with python incompatibilities when working on the code. However
you can still use ``pip3 install .`` in the project's directory to
install the package locally.

If you choose to use the virtual environment, `install poetry
<https://python-poetry.org/docs/#installation>`_ since that's how
*Raider* was developed.

Once poetry is installed, you can prepare the virtual environment and
switch to it to work with *Raider*:

.. code-block:: bash

   cd raider
   poetry install
   poetry shell


And now you're working inside the virtual environment, and *Raider*
should be available here.
