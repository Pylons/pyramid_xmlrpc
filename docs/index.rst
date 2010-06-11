Documentation for repoze.bfg.xmlrpc
===================================

XML-RPC support for the :mod:`repoze.bfg` web framework.

:mod:`repoze.bfg.xmlrpc` Installation
-------------------------------------

:mod:`repoze.bfg.xmlrpc` is a package that ships outside the main
:mod:`repoze.bfg` distribution.  To install the package, use
``easy_install``::

  easy_install -i http://dist.repoze.org/bfgsite/simple repoze.bfg.xmlrpc

Or obtain the packge via `http://svn.repoze.org/repoze.bfg.xmlrpc
<http://pypi.python.org/pypi/repoze.bfg.xmlrpc>`_ and use ``setup.py
install``.

:mod:`repoze.bfg.xmlrpc` Usage
------------------------------

XML-RPC allows you to expose one or more methods at a particular URL.
:mod:`repoze.bfg.xmlrpc` has a simple usage pattern for exposing a 
single method at a particular url, and a more complicated one for 
when you want to expose multiple methods at a particular URL.

Exposing a single method
~~~~~~~~~~~~~~~~~~~~~~~~

Create a function in the form below.  The function will be meant to be
called with positional parameters from an XML-RPC request.

.. code-block:: python
   :linenos:

   def say_hello(context, name):
       return 'Hello, %s' % name

Then add the :func:`~repoze.bfg.xmlrpc.xmlrpc_view` decorator to the function.

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

Exposing multiple methods
~~~~~~~~~~~~~~~~~~~~~~~~~

If you have multiple methods to expose at a particular url, you should
group them together in a class. Think of this class in the same way
as you would when you implement a normal :mod:`repoze.bfg` view as a 
class rather than a function.

The methods of the class will be those exposed as methods to XML-RPC.
Not that XML-RPC only supports positional parameters.

To make this view class handle incoming XML-RPC requests, you simply 
need to subclass the :class:`~repoze.bfg.xmlrpc.XMLRPCView` class.
:class:`~repoze.bfg.xmlrpc.XMLRPCView` provides a
:meth:`~repoze.bfg.xmlrpc.XMLRPCView.__call__` method, so make sure
that your class doesn't provide one!

For example:

.. code-block:: python
   :linenos:

   from repoze.bfg.xmlrpc import XMLRPCView

   class MyXMLRPCStuff(XMLRPCView)
   
      def say_hello(self):
          return 'Hello, %s' % name

      def say_goobye(self):
          return 'Goodbye, cruel world'

This class can then be registered with :mod:`repoze.bfg` as a 
normal view: 

.. code-block:: xml
   :linenos:

   <bfg:view
     name="RPC2"
     view=".views.MyXMLRPCStuff"
     for="*"
     />

The methods exposed by this view can now be used by any XML-RPC
client:

.. code-block:: python
   :linenos:

   >>> from xmlrpclib import ServerProxy
   >>> s = ServerProxy('http://localhost:6543/RPC2')
   >>> s.say_hello('Chris')
   Hello, Chris
   >>> s.say_goodbye()
   Goodbye, cruel world

.. _api:

API Documentation for :mod:`repoze.bfg.xmlrpc`
----------------------------------------------

.. automodule:: repoze.bfg.xmlrpc

  .. autofunction:: xmlrpc_view

  .. autoclass:: XMLRPCView
     :members: __call__

  .. autofunction:: xmlrpc_marshal

  .. autofunction:: xmlrpc_response

  .. autofunction:: parse_xmlrpc_request


Indices and tables
------------------

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
