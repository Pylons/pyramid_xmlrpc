import inspect
import xmlrpclib

from zope.interface import implements
from zope.interface import alsoProvides
from zope.interface import Interface
from zope.interface import providedBy

from pyramid.interfaces import IViewClassifier
from pyramid.interfaces import IView
from pyramid.interfaces import IViewMapperFactory

from pyramid.events import NewRequest
from pyramid.exceptions import NotFound
from pyramid.exceptions import Forbidden
from pyramid.traversal import traverse
from pyramid.security import has_permission
from pyramid.view import view_config

# MapplyViewMapper is not an API; it may be moved into another package later

class MapplyViewMapper(object): 
    implements(IViewMapperFactory)
    def __init__(self, **kw):
        self.attr = kw.get('attr')

    def __call__(self, view):
        attr = self.attr
        if inspect.isclass(view):
            def _class_view(context, request):
                params = getattr(request, 'xmlrpc_params', ())
                keywords = dict(request.params.items())
                if request.matchdict:
                    keywords.update(request.matchdict)
                if attr is None:
                    inst = view(request)
                    response = self.mapply(inst, params, keywords)
                else:
                    inst = view(request)
                    response = self.mapply(getattr(inst, attr), params,
                                           keywords)
                request.__view__ = inst
                return response
            mapped_view = _class_view
        else:
            def _nonclass_view(context, request):
                params = (request,) + getattr(request, 'xmlrpc_params', ())
                keywords = dict(request.params.items())
                if request.matchdict:
                    keywords.update(request.matchdict)
                if attr is None:
                    response = self.mapply(view, params, keywords)
                else:
                    response = self.mapply(getattr(view, attr), params,
                                           keywords)
                return response
            mapped_view = _nonclass_view

        return mapped_view

    def mapply(self, ob, positional, keyword):

        f = ob
        im = False

        if hasattr(f, 'im_func'):
            im = True

        elif not hasattr(f, 'func_defaults'):
            if hasattr(f, '__call__'):
                f = f.__call__
                if hasattr(f, 'im_func'):
                    im = True

        if im:
            f = f.im_func
            c = f.func_code
            defaults = f.func_defaults
            names = c.co_varnames[1:c.co_argcount]
        else:
            defaults = f.func_defaults
            c = f.func_code
            names = c.co_varnames[:c.co_argcount]

        nargs = len(names)
        args = []
        if positional:
            positional = list(positional)
            if len(positional) > nargs:
                raise TypeError('too many arguments')
            args = positional

        get = keyword.get
        nrequired = len(names) - (len(defaults or ()))
        for index in range(len(args), len(names)):
            name = names[index]
            v = get(name, args)
            if v is args:
                if index < nrequired:
                    raise TypeError('argument %s was omitted' % name)
                else:
                    v = defaults[index-nrequired]
            args.append(v)

        args = tuple(args)
        return ob(*args)

def parse_xmlrpc_request(request):
    """ Deserialize the body of a request from an XML-RPC request
    document into a set of params and return a two-tuple.  The first
    element in the tuple is the method params as a sequence, the
    second element in the tuple is the method name."""
    if request.content_length > (1 << 23):
        # protect from DOS (> 8MB body), webob will only read CONTENT_LENGTH
        # bytes when body is accessed, so no worries about getting a
        # bogus CONTENT_LENGTH header
        raise ValueError('Body too large (%s bytes)' % request.content_length)
    params, method = xmlrpclib.loads(request.body, use_datetime=True)
    return params, method

class xmlrpc_config(view_config):
    """ This decorator acts almost exactly like
    :class:`pyramid.view.view_config` but it produces a view configuration
    which can call an XMLRPC callable rather than a standard Pyramid view
    callable.

    An XMLRPC callable is one which accepts a variable argument list, which
    will be populated by items available from the XMLRPC params list,
    ``request.params`` and ``request.matchdict``.  Its first argument must be
    ``request``, the other arguments will be populated from the available
    parameters.

    E.g.::

      from pyramid.xmlrpc import xmlrpc_config

      @xmlrpc_config()
      def say(request, what):
          return {'say':what}
    """
    def __init__(self, name='', request_type=None, for_=None, permission=None,
                 route_name=None, request_method=None, request_param=None,
                 containment=None, attr=None, wrapper=None, xhr=False,
                 accept=None, header=None, path_info=None, custom_predicates=(),
                 context=None, view_mapper=MapplyViewMapper,
                 renderer='xmlrpc'):
        self.name = name
        if request_type is None:
            request_type = IXMLRPCRequest
        self.request_type = request_type
        self.context = context or for_
        self.permission = permission
        self.route_name = route_name
        self.request_method = request_method
        self.request_param = request_param
        self.containment = containment
        self.attr = attr
        self.wrapper = wrapper
        self.xhr = xhr
        self.accept = accept
        self.header = header
        self.path_info = path_info
        self.custom_predicates = custom_predicates
        self.renderer = renderer
        self.view_mapper = view_mapper
        self.custom_predicates = custom_predicates

def xmlrpc_renderer_factory(info):
    def _render(value, system):
        request = system.get('request')
        if request is not None:
            if not hasattr(request, 'response_content_type'):
                request.response_content_type = 'text/xml'
        if isinstance(value, xmlrpclib.Fault):
            return xmlrpclib.dumps(value)
        else:
            return xmlrpclib.dumps((value,),  methodresponse=True)
    return _render

def xmlrpc_traversal_view(context, request):
    # duplicate some logic from router to do Zope-style traversal and view
    # lookup.
    params, method = request.xmlrpc_params, request.xmlrpc_method
    names = method.split('.')
    info = traverse(context, '/'.join(names))
    inner_context = info['context']
    view_name = info['view_name']
    repr_permission = request.registry.settings.get(
        'pyramid_xmlrpc.repr_permission', 'view')

    if view_name == '__call__':
        view_name = ''

    if view_name == '__repr__':
        def view(context, request):
            if has_permission(context, request, repr_permission):
                return repr(context)
            raise Forbidden('No "%s" permission on context' % repr_permission)
    else:
        provides = [IViewClassifier] + map(providedBy,
                                           (request, inner_context))
        reg = request.registry
        view = reg.adapters.lookup(provides, IView, view_name, default=None)

    if getattr(view, '__original_view__', None) is xmlrpc_traversal_view:
        view = None

    if view is None:
        raise NotFound(method)

    request.__dict__.update(info)
    return view(inner_context, request)

class IXMLRPCRequest(Interface):
    # marker interface
    pass

def _set_xmlrpc_params(event, override):
    request = event.request
    headers = request.headers
    if (request.content_type == 'text/xml'
        and request.method == 'POST'
        and not 'soapaction' in headers
        and not 'x-pyramid-avoid-xmlrpc' in headers):
        params, method = parse_xmlrpc_request(request)
        request.xmlrpc_params, request.xmlrpc_method = params, method
        alsoProvides(request, IXMLRPCRequest)
        if override:
            request.override_renderer = 'xmlrpc'
        return True
    return False

def set_xmlrpc_params_omnipresent(event):
    return _set_xmlrpc_params(event, override=True)

def set_xmlrpc_params(event):
    return _set_xmlrpc_params(event, override=False)

def limited(config):
    """ ``config.include`` target which sets up limited XML-RPC access to an
    application.  Only views configured via ``pyramid_xmlrpc.xmlrpc_config``
    will be exposed to the world."""
    config.add_renderer('xmlrpc', xmlrpc_renderer_factory)
    config.add_subscriber(set_xmlrpc_params, NewRequest)

def omnipresent(config):
    """ ``config.include`` target which sets up omnipresent (Zope-style)
    XML-RPC access to an applicaton.  Any view configured that uses a
    renderer will be accessible via XML-RPC.  Traversal over the resource
    tree via xmlrpc will also work."""
    config.add_renderer('xmlrpc', xmlrpc_renderer_factory)
    config.add_subscriber(set_xmlrpc_params_omnipresent, NewRequest)
    config.add_view(
        xmlrpc_traversal_view,
        renderer='xmlrpc',
        request_type=IXMLRPCRequest,
        )

includeme = limited
