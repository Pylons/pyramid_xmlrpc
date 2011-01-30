import unittest
from pyramid import testing

class TestMapplyViewMapper(unittest.TestCase):
    def _makeOne(self, **kw):
        from pyramid_xmlrpc import MapplyViewMapper
        return MapplyViewMapper(**kw)

    def test___call__isfunc_no_xmlrpc_params_no_attr(self):
        data = '123'
        def view(request):
            return data
        context = testing.DummyResource()
        request = testing.DummyRequest()
        mapper = self._makeOne()
        result = mapper(view)(context, request)
        self.assertEqual(result, data)

    def test___call__isfunc_no_xmlrpc_params_with_attr(self):
        view = lambda *arg: 'wrong'
        data = '123'
        def foo(request):
            return data
        view.foo = foo
        context = testing.DummyResource()
        request = testing.DummyRequest()
        mapper = self._makeOne(attr='foo')
        result = mapper(view)(context, request)
        self.assertEqual(result, data)

    def test___call__isfunc_with_xmlrpc_params(self):
        def view(request, a, b):
            return a, b
        context = testing.DummyResource()
        request = testing.DummyRequest()
        request.xmlrpc_params = ('a', 'b')
        mapper = self._makeOne()
        result = mapper(view)(context, request)
        self.assertEqual(result, ('a', 'b'))

    def test___call__isfunc_with_xmlrpc_params_and_matchdict(self):
        def view(request, a, b, c=1):
            return a, b, c
        context = testing.DummyResource()
        request = testing.DummyRequest()
        request.xmlrpc_params = ('a', 'b')
        request.matchdict = dict(c='2')
        mapper = self._makeOne()
        result = mapper(view)(context, request)
        self.assertEqual(result, ('a', 'b', '2'))

    def test___call__isclass_no_xmlrpc_params_no_attr(self):
        data = '123'
        class view(object):
            def __init__(self, request):
                pass
            def __call__(self):
                return data
        context = testing.DummyResource()
        request = testing.DummyRequest()
        mapper = self._makeOne()
        result = mapper(view)(context, request)
        self.assertEqual(result, data)
        self.assertEqual(request.__view__.__class__, view)

    def test___call__isclass_no_xmlrpc_params_with_attr(self):
        view = lambda *arg: 'wrong'
        data = '123'
        class view(object):
            def __init__(self, request):
                pass
            def index(self):
                return data
        context = testing.DummyResource()
        request = testing.DummyRequest()
        mapper = self._makeOne(attr='index')
        result = mapper(view)(context, request)
        self.assertEqual(result, data)
        self.assertEqual(request.__view__.__class__, view)

    def test___call__isclass_with_xmlrpc_params(self):
        class view(object):
            def __init__(self, request):
                pass
            def __call__(self, a, b):
                return a, b
        context = testing.DummyResource()
        request = testing.DummyRequest()
        request.xmlrpc_params = ('a', 'b')
        mapper = self._makeOne()
        result = mapper(view)(context, request)
        self.assertEqual(result, ('a', 'b'))

    def test___call__isclass_with_xmlrpc_params_and_matchdict(self):
        class view(object):
            def __init__(self, request):
                pass
            def __call__(self, a, b, c=1):
                return a, b, c
        context = testing.DummyResource()
        request = testing.DummyRequest()
        request.xmlrpc_params = ('a', 'b')
        request.matchdict = dict(c='2')
        mapper = self._makeOne()
        result = mapper(view)(context, request)
        self.assertEqual(result, ('a', 'b', '2'))

    def test_mapply_toomanyargs(self):
        def aview(one, two): pass
        mapper = self._makeOne()
        self.assertRaises(TypeError, mapper.mapply, aview, (1, 2, 3), {})

    def test_mapply_all_kwarg_arg_omitted(self):
        def aview(one, two): pass
        mapper = self._makeOne()
        self.assertRaises(TypeError, mapper.mapply, aview, (), dict(one=1))

    def test_mapply_all_kwarg_arg_omitted_with_default(self):
        def aview(one, two=2):
            return one, two
        mapper = self._makeOne()
        result = mapper.mapply(aview, (), dict(one=1))
        self.assertEqual(result, (1, 2))

    def test_mapply_all_kwarg(self):
        def aview(one, two):
            return one, two
        mapper = self._makeOne()
        result = mapper.mapply(aview, (), dict(one=1, two=2))
        self.assertEqual(result, (1, 2))

    def test_mapply_instmethod(self):
        mapper = self._makeOne()
        result = mapper.mapply(self._aview, ('a',), {})
        self.assertEqual(result, 'a')

    def test_mapply_inst(self):
        class Foo(object):
            def __call__(self, a):
                return a
        foo = Foo()
        mapper = self._makeOne()
        result = mapper.mapply(foo, ('a',), {})
        self.assertEqual(result, 'a')

    def _aview(self, a):
        return a

class Test_parse_xmlrpc_request(unittest.TestCase):
    def _callFUT(self, request):
        from pyramid_xmlrpc import parse_xmlrpc_request
        return parse_xmlrpc_request(request)

    def test_normal(self):
        import xmlrpclib
        param = 1
        packet = xmlrpclib.dumps((param,), methodname='__call__')
        request = testing.DummyRequest()
        request.body = packet
        request.content_length = len(packet)
        params, method = self._callFUT(request)
        self.assertEqual(params[0], param)
        self.assertEqual(method, '__call__')

    def test_toobig(self):
        request = testing.DummyRequest()
        request.content_length = 1 << 24
        self.assertRaises(ValueError, self._callFUT, request)

class Test_xmlrpc_config(unittest.TestCase):
    def _makeOne(self, **kw):
        from pyramid_xmlrpc import xmlrpc_config
        return xmlrpc_config(**kw)

    def test_it_no_request_type(self):
        from pyramid_xmlrpc import IXMLRPCRequest
        inst = self._makeOne()
        self.assertEqual(inst.request_type, IXMLRPCRequest)

    def test_it_with_request_type(self):
        inst = self._makeOne(request_type=1)
        self.assertEqual(inst.request_type, 1)

class Test_xmlrpc_renderer_factory(unittest.TestCase):
    def _callFUT(self, info):
        from pyramid_xmlrpc import xmlrpc_renderer_factory
        return xmlrpc_renderer_factory(info)

    def test_render_normalvalue(self):
        import xmlrpclib
        renderer = self._callFUT(None)
        request = testing.DummyRequest()
        result = renderer('one', dict(request=request))
        self.assertEqual(result, xmlrpclib.dumps(('one',),
                                                 methodresponse=True)) 

    def test_render_Fault(self):
        import xmlrpclib
        renderer = self._callFUT(None)
        request = testing.DummyRequest()
        fault = xmlrpclib.Fault('1', '1')
        result = renderer(fault, dict(request=request))
        self.assertEqual(result, xmlrpclib.dumps(fault))

class Test_xmlrpc_traversal_view(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp()

    def tearDown(self):
        testing.tearDown()

    def _callFUT(self, context, request):
        from pyramid_xmlrpc import xmlrpc_traversal_view
        return xmlrpc_traversal_view(context, request)

    def test_no_permission(self):
        from pyramid.exceptions import Forbidden
        def theview(request): pass
        self.config.testing_securitypolicy('fred', permissive=False)
        self.config.add_view(theview, name='foo', permission='view')
        request = testing.DummyRequest()
        request.xmlrpc_params = ()
        request.xmlrpc_method = 'foo'
        context = testing.DummyResource()
        self.assertRaises(Forbidden, self._callFUT, context, request)

    def test_has_permission(self):
        def theview(request):
            return '123'
        self.config.testing_securitypolicy('fred', permissive=True)
        self.config.add_view(theview, name='foo', permission='view')
        request = testing.DummyRequest()
        request.xmlrpc_params = ()
        request.xmlrpc_method = 'foo'
        context = testing.DummyResource()
        result = self._callFUT(context, request)
        self.assertEqual(result, '123')

    def test_unprotected(self):
        def theview(request):
            return '123'
        self.config.testing_securitypolicy('fred', permissive=False)
        self.config.add_view(theview, name='foo')
        request = testing.DummyRequest()
        request.xmlrpc_params = ()
        request.xmlrpc_method = 'foo'
        context = testing.DummyResource()
        result = self._callFUT(context, request)
        self.assertEqual(result, '123')
        self.assertEqual(request.view_name, 'foo')
        
    def test_recursion_protection(self):
        from pyramid.exceptions import NotFound
        from pyramid_xmlrpc import xmlrpc_traversal_view
        self.config.testing_securitypolicy('fred', permissive=True)
        self.config.add_view(xmlrpc_traversal_view, name='foo',
                             permission='view')
        request = testing.DummyRequest()
        request.xmlrpc_params = ()
        request.xmlrpc_method = 'foo'
        context = testing.DummyResource()
        self.assertRaises(NotFound, self._callFUT, context, request)

    def test_view_name_is___repr__security_pass(self):
        request = testing.DummyRequest()
        request.xmlrpc_params = ()
        request.xmlrpc_method = '__repr__'
        context = testing.DummyResource()
        expected = repr(context)
        result = self._callFUT(context, request)
        self.assertEqual(result, expected)

    def test_view_name_is___repr__security_fail(self):
        from pyramid.exceptions import Forbidden
        request = testing.DummyRequest()
        request.xmlrpc_params = ()
        request.xmlrpc_method = '__repr__'
        self.config.testing_securitypolicy(permissive=False)
        request.registry.settings['pyramid_xmlrpc.repr_permission'] = 'view'
        context = testing.DummyResource()
        self.assertRaises(Forbidden, self._callFUT, context, request)

    def test_view_name_is___call__(self):
        def theview(request):
            return '123'
        self.config.add_view(theview)
        request = testing.DummyRequest()
        request.xmlrpc_params = ()
        request.xmlrpc_method = '__call__'
        context = testing.DummyResource()
        result = self._callFUT(context, request)
        self.assertEqual(result, '123')

class Test__set_xmlrpc_params(unittest.TestCase):
    def _callFUT(self, event, override):
        from pyramid_xmlrpc import _set_xmlrpc_params
        return _set_xmlrpc_params(event, override)

    def test_false_not_text_xml(self):
        request = testing.DummyRequest()
        request.content_type = 'not/textxml'
        request.method = 'POST'
        request.headers = {}
        event = DummyEvent()
        event.request = request
        result = self._callFUT(event, False)
        self.assertEqual(result, False)

    def test_false_not_post(self):
        request = testing.DummyRequest()
        request.content_type = 'text/xml'
        request.method = 'GET'
        request.headers = {}
        event = DummyEvent()
        event.request = request
        result = self._callFUT(event, False)
        self.assertEqual(result, False)

    def test_false_soapaction(self):
        request = testing.DummyRequest()
        request.content_type = 'text/xml'
        request.method = 'POST'
        request.headers = {'soapaction':'true'}
        event = DummyEvent()
        event.request = request
        result = self._callFUT(event, False)
        self.assertEqual(result, False)

    def test_false_avoid_xmlrpc(self):
        request = testing.DummyRequest()
        request.content_type = 'text/xml'
        request.method = 'POST'
        request.headers = {'x-pyramid-avoid-xmlrpc':'true'}
        event = DummyEvent()
        event.request = request
        result = self._callFUT(event, False)
        self.assertEqual(result, False)

    def test_true_no_override(self):
        import xmlrpclib
        from pyramid_xmlrpc import IXMLRPCRequest
        request = testing.DummyRequest()
        request.content_type = 'text/xml'
        request.method = 'POST'
        request.headers = {}
        request.body = xmlrpclib.dumps(('a',))
        event = DummyEvent()
        event.request = request
        result = self._callFUT(event, False)
        self.assertEqual(result, True)
        self.failUnless(IXMLRPCRequest.providedBy(request))
        self.assertEqual(request.xmlrpc_params, ('a',))
        self.assertEqual(request.xmlrpc_method, None)
        self.assertEqual(getattr(request, 'override_renderer', None), None)

    def test_true_with_override(self):
        import xmlrpclib
        from pyramid_xmlrpc import IXMLRPCRequest
        request = testing.DummyRequest()
        request.content_type = 'text/xml'
        request.method = 'POST'
        request.headers = {}
        request.body = xmlrpclib.dumps(('a',))
        event = DummyEvent()
        event.request = request
        result = self._callFUT(event, True)
        self.assertEqual(result, True)
        self.failUnless(IXMLRPCRequest.providedBy(request))
        self.assertEqual(request.xmlrpc_params, ('a',))
        self.assertEqual(request.xmlrpc_method, None)
        self.assertEqual(request.override_renderer, 'xmlrpc')

class Test_set_xmlrpc_params_omnipresent(unittest.TestCase):
    def _callFUT(self, event):
        from pyramid_xmlrpc import set_xmlrpc_params_omnipresent
        return set_xmlrpc_params_omnipresent(event)

    def test_it(self):
        import xmlrpclib
        from pyramid_xmlrpc import IXMLRPCRequest
        request = testing.DummyRequest()
        request.content_type = 'text/xml'
        request.method = 'POST'
        request.headers = {}
        request.body = xmlrpclib.dumps(('a',))
        event = DummyEvent()
        event.request = request
        result = self._callFUT(event)
        self.assertEqual(result, True)
        self.failUnless(IXMLRPCRequest.providedBy(request))
        self.assertEqual(request.xmlrpc_params, ('a',))
        self.assertEqual(request.xmlrpc_method, None)
        self.assertEqual(request.override_renderer, 'xmlrpc')

class Test_set_xmlrpc_params(unittest.TestCase):
    def _callFUT(self, event):
        from pyramid_xmlrpc import set_xmlrpc_params
        return set_xmlrpc_params(event)

    def test_it(self):
        import xmlrpclib
        from pyramid_xmlrpc import IXMLRPCRequest
        request = testing.DummyRequest()
        request.content_type = 'text/xml'
        request.method = 'POST'
        request.headers = {}
        request.body = xmlrpclib.dumps(('a',))
        event = DummyEvent()
        event.request = request
        result = self._callFUT(event)
        self.assertEqual(result, True)
        self.failUnless(IXMLRPCRequest.providedBy(request))
        self.assertEqual(request.xmlrpc_params, ('a',))
        self.assertEqual(request.xmlrpc_method, None)
        self.assertEqual(getattr(request, 'override_renderer', None), None)

class Test_limited(unittest.TestCase):
    def _callFUT(self, config):
        from pyramid_xmlrpc import limited
        return limited(config)

    def test_it(self):
        from pyramid_xmlrpc import xmlrpc_renderer_factory
        from pyramid_xmlrpc import set_xmlrpc_params
        from pyramid.events import NewRequest
        config = DummyConfig()
        self._callFUT(config)
        self.assertEqual(config.renderers['xmlrpc'], xmlrpc_renderer_factory)
        self.assertEqual(config.views, [])
        self.assertEqual(config.subscribers, [(set_xmlrpc_params, NewRequest)])

class Test_omnipresent(unittest.TestCase):
    def _callFUT(self, config):
        from pyramid_xmlrpc import omnipresent
        return omnipresent(config)

    def test_it(self):
        from pyramid_xmlrpc import xmlrpc_renderer_factory
        from pyramid_xmlrpc import set_xmlrpc_params_omnipresent
        from pyramid_xmlrpc import IXMLRPCRequest
        from pyramid_xmlrpc import xmlrpc_traversal_view
        from pyramid.events import NewRequest
        config = DummyConfig()
        self._callFUT(config)
        self.assertEqual(config.renderers['xmlrpc'], xmlrpc_renderer_factory)
        self.assertEqual(config.views,
                         [(xmlrpc_traversal_view,
                           {'request_type':IXMLRPCRequest,
                            'renderer':'xmlrpc'})])
        self.assertEqual(config.subscribers, [(set_xmlrpc_params_omnipresent,
                                               NewRequest)])

class DummyEvent(object):
    pass

class DummyConfig(object):
    def __init__(self):
        self.renderers = {}
        self.subscribers = []
        self.views = []

    def add_renderer(self, name, factory):
        self.renderers[name] = factory

    def add_subscriber(self, impl, type):
        self.subscribers.append((impl, type))
        
    def add_view(self, view, **kw):
        self.views.append((view, kw))
