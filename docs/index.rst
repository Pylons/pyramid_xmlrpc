Documentation for repoze.bfg.xmlrpc
===================================

XML-RPC support for the :mod:`repoze.bfg` web framework.

:mod:`repoze.bfg.xmlrpc` Installation
-------------------------------------

:mod:`repoze.bfg.xmlrpc` is a package that ships outside the main
:mod:`repoze.bfg` distribution.  To install the package, use
``easy_install``::

  easy_install -i http://dist.repoze.org/bfgsite/simple repoze.bfg.xmrpc

Or obtain the packge via `http://svn.repoze.org/repoze.bfg.xmlrpc
<http://svn.repoze.org/rpoze.bfg.xmlrpc>`_ and use ``setup.py
install``.

:mod:`repoze.bfg.xmlrpc` Usage
------------------------------

Create a function in the form below.  The function will be meant to be
called with positional parameters from an XML-RPC request.

.. code-block:: python
   :linenos:

   def say_hello(context, name):
       return 'Hello, %s' % name

Then add the ``@xmlrpc_view`` decorator to the function.

.. code-block:: python
   :linenos:

   from repoze.bfg.xmlrpc import xmlrpc_view

   @xmlrpc_view
   def say_hello(context, name):
       return 'Hello, %s' % name

Then configure your application registry to point to the ``say_hello``
view.

.. code-block:: xml
   :linenos:

   <bfg:view
     name="say_hello"
     view=".views.say_hello"
     for="*"
     />

Then call the function via an XML-RPC client.  Note that any XML-RPC
``methodName`` will be ignored; you must point the client directly at
the view URL; traversal doesn't work from there.

.. code-block:: python
   :linenos:

   >>> from xmlrpclib import ServerProxy
   >>> s = ServerProxy('http://localhost:6543/say_hello')
   >>> s('Chris')
   Hello, Chris

.. _api:

API Documentation for :mod:`repoze.bfg.xmlrpc`
----------------------------------------------

.. automodule:: repoze.bfg.xmlrpc

  .. autofunction:: xmlrpc_view

  .. autofunction:: xmlrpc_marshal

  .. autofunction:: xmlrpc_response

  .. autofunction:: parse_xmlrpc_request


Indices and tables
------------------

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
