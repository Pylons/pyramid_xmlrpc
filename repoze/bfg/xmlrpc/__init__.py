import xmlrpclib
import webob

def xmlrpc_marshal(data):
    """ Marshal a Python data structure into an XML document suitable
    for use as an XML-RPC response and return the document.  If
    ``data`` is an ``xmlrpclib.Fault`` instance, it will be marshalled
    into a suitable XML-RPC fault response."""
    if isinstance(data, xmlrpclib.Fault):
        return xmlrpclib.dumps(data)
    else:
        return xmlrpclib.dumps((data,),  methodresponse=True)

def xmlrpc_response(data):
    """ Marshal a Python data structure into a webob ``Response``
    object with a body that is an XML document suitable for use as an
    XML-RPC response with a content-type of ``text/xml`` and return
    the response."""
    xml = xmlrpc_marshal(data)
    response = webob.Response(xml)
    response.content_type = 'text/xml'
    response.content_length = len(xml)
    return response

def parse_xmlrpc_request(request):
    """ Deserialize the body of a request from an XML-RPC request
    document into a set of params and return a two-tuple.  The first
    element in the tuple is the method params as a sequence, the
    second element in the tuple is the method name."""
    if request.content_length > (1 << 23):
        # protect from DOS (> 8MB body)
        raise ValueError('Body too large (%s bytes)' % request.content_length)
    params, method = xmlrpclib.loads(request.body)
    return params, method

def xmlrpc_view(wrapped):
    """ This decorator turns functions which accept params and return Python
    structures into functions suitable for use as bfg views that speak XML-RPC.
    The decorated function must accept a ``context`` argument and zero or
    more positional arguments (conventionally named ``*params``).

    E.g.::

      from repoze.bfg.xmlrpc import xmlrpc_view

      @xmlrpc_view
      def say(context, what):
          if what == 'hello'
              return {'say':'Hello!'}
          else:
              return {'say':'Goodbye!'}

    Equates to::

      from repoze.bfg.xmlrpc import parse_xmlrpc_request
      from repoze.bfg.xmlrpc import xmlrpc_response

      def say_view(context, request):
          params, method = parse_xmlrpc_request(request)
          return say(context, *params)

      def say(context, what):
          if what == 'hello'
              return {'say':'Hello!'}
          else:
              return {'say':'Goodbye!'}

    Note that if you use :class:`~repoze.bfg.view.bfg_view`, you must
    decorate your view function in the following order for it to be
    recognized by the convention machinery as a view::

      @bfg_view(name='say')
      @xmlrpc_view
      def say(context, what):
          if what == 'hello'
              return {'say':'Hello!'}
          else:
              return {'say':'Goodbye!'}

    In other words do *not* decorate it in :func:`~repoze.bfg.xmlrpc.xmlrpc_view`,
    then :class:`~repoze.bfg.view.bfg_view`; it won't work.
    """
    
    def _curried(context, request):
        params, method = parse_xmlrpc_request(request)
        value = wrapped(context, *params)
        return xmlrpc_response(value)
    _curried.__name__ = wrapped.__name__
    _curried.__grok_module__ = wrapped.__module__ # r.bfg.convention support

    return _curried
    
class XMLRPCView:
    """A base class for a view that serves multiple methods by XML-RPC.

    Subclass and add your methods as described in the documentation.
    """

    def __init__(self,context,request):
        self.context = context
        self.request = request

    def __call__(self):
        """
        This method de-serializes the XML-RPC request and
        dispatches the resulting method call to the correct
        method on the :class:`~repoze.bfg.xmlrpc.XMLRPCView`
        subclass instance.

        .. warning::
          Do not override this method in any subclass if you
          want XML-RPC to continute to work!
          
        """
        params, method = parse_xmlrpc_request(self.request)
        return xmlrpc_response(getattr(self,method)(*params))
