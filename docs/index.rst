Documentation for repoze.bfg.xmlrpc
===================================

XML-RPC support for the :mod:`repoze.bfg` web framework.

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

.. toctree::
   :maxdepth: 2

   api.rst


Topic A
-------

Explain topic.


Indices and tables
------------------

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
