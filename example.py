'''
pip install Paste
pip install PasteDeploy
pip install eventlet
pip install routes
pip install webob

python example.py

GET 127.0.0.1/root/test
POST 127.0.0.1/root/test/create
GET 127.0.0.1/root/instance/list_
...

'''
import eventlet
from eventlet import wsgi
from paste.deploy import loadapp
import routes
import routes.middleware as middleware
import webob.dec
import webob.exc
import json

class Controller(object):
    def list_(self, req):
        res = webob.Response(json.dumps({"1": 111, "2": 222}))
        res.status = 201		
        return res
		
    def detail(self, req):
        return "This is detail"

	
class TestController(object):

    def index(self, req):
        return 'GET'

    def create(self, req):
        return 'POST'

    def delete(self, req):
        return 'DELETE'

    def update(self, req):
        print(req.GET)
        return 'PUT'


class TestResource(object):
    def __init__(self, controller):
        self.controller = controller()

    @webob.dec.wsgify
    def __call__(self, req):
        print("CCCC")
        match = req.environ['wsgiorg.routing_args'][1]
        action = match['action']
        print("action =", action)
        if hasattr(self.controller, action):
            method = getattr(self.controller, action)
            return method(req)
        return webob.exc.HTTPNotFound()


class TestApplication(object):
    def __init__(self):
        self.mapper = routes.Mapper()
        
        self.mapper.connect("/test", action="index", controller=TestResource(TestController))
        self.mapper.connect("/test/{action}", controller=TestResource(TestController), conditions={'method':['POST']})
       
        self.mapper.connect("/instance/{action}", controller=TestResource(Controller), conditions={'method':['POST', 'GET']})
        
        self.router = middleware.RoutesMiddleware(self.dispatch, self.mapper)

    @webob.dec.wsgify
    def __call__(self, req):
        return self.router

    @classmethod
    def factory(cls, global_conf, **local_conf):
        return cls()

    @staticmethod
    @webob.dec.wsgify
    def dispatch(req):
        print("DDDD")
        match = req.environ['wsgiorg.routing_args'][1]
        return match['controller'] if match else webob.exc.HTTPNotFound()

		
if '__main__' == __name__:
    application = loadapp('config:d:/config.ini')  #配置文件放在d:/config.ini
    server = eventlet.spawn(wsgi.server,
                            eventlet.listen(('0.0.0.0', 9009)), application)
    server.wait()