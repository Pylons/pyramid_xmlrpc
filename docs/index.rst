Documentation for pyramid_xmlrpc
================================

XML-RPC support for the :mod:`pyramid` web framework.

:mod:`pyramid_xmlrpc` Installation
-------------------------------------

:mod:`pyramid_xmlrpc` is a package that ships outside the main
:mod:`pyramid` distribution.  To install the package, use
``easy_install``::

  easy_install pyramid_xmlrpc

Or obtain the packge via `http://github.com/Pylons/pyramid_xmlrpc
<http://github.com/Pylons/pyramid_xmlrpc>`_ and use ``setup.py
install``.

:mod:`pyramid_xmlrpc` Usage
------------------------------

XML-RPC allows you to expose one or more methods at a particular URL.
:mod:`pyramid_xmlrpc` has a simple usage pattern for exposing a single method
at a particular url, and a more complicated one for when you want to expose
multiple methods at a particular URL.

Exposing a single method
~~~~~~~~~~~~~~~~~~~~~~~~

Create a function in the form below.  The function will be meant to be called
with positional parameters from an XML-RPC request.

.. code-block:: python
   :linenos:

   def say_hello(context, name):
       return 'Hello, %s' % name

Then add the :func:`~pyramid_xmlrpc.xmlrpc_view` decorator to the function.

.. code-block:: python
   :linenos:

   from pyramid_xmlrpc import xmlrpc_view

   @xmlrpc_view
   def say_hello(context, name):
       return 'Hello, %s' % name

Then configure your application registry to point to the ``say_hello``
view.

Using imperative code in your application's startup configuration:

.. code-block:: python
   :linenos:

   from mypackage import say_hello
   config.add_view(say_hello, name='say_hello')

Using ZCML:

.. code-block:: xml
   :linenos:

   <view
     name="say_hello"
     view=".views.say_hello"
     for="*"
     />

Or using a ``view_config`` decorator:

.. code-block:: python
   :linenos:

   from pyramid_xmlrpc import xmlrpc_view
   from pyramid.view import view_config

   @view_config(name='say_hello')
   @xmlrpc_view
   def say_hello(context, name):
       return 'Hello, %s' % name

Then call the function via an XML-RPC client.  Note that any XML-RPC
``methodName`` will be ignored; you must point the client directly at the view
URL; traversal doesn't work from there.

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
as you would when you implement a normal :mod:`pyramid` view as a 
class rather than a function.

The methods of the class will be those exposed as methods to XML-RPC.
Not that XML-RPC only supports positional parameters.

To make this view class handle incoming XML-RPC requests, you simply 
need to subclass the :class:`~pyramid_xmlrpc.XMLRPCView` class.
:class:`~pyramid_xmlrpc.XMLRPCView` provides a
:meth:`~pyramid_xmlrpc.XMLRPCView.__call__` method, so make sure
that your class doesn't provide one!

For example:

.. code-block:: python
   :linenos:

   from pyramid_xmlrpc import XMLRPCView

   class MyXMLRPCStuff(XMLRPCView):
   
      def say_hello(self, name):
          return 'Hello, %s' % name

      def say_goobye(self):
          return 'Goodbye, cruel world'

This class can then be registered with :mod:`pyramid` as a 
normal view.

Using imperative code in your application's startup configuration:

.. code-block:: python
   :linenos:

   from mypackage import MyXMLRPCStuff
   config.add_view(MyXMLRPCStuff, name='RPC2')

Via ZCML:

.. code-block:: xml
   :linenos:

   <view
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

API Documentation for :mod:`pyramid_xmlrpc`
----------------------------------------------

.. automodule:: pyramid_xmlrpc

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
