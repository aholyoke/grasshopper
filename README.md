# The Grasshopper Python Microframework

### Design philosophy
* Favour intuitive design over saving key-strokes
* No python-foo/magic
* Simple internal data structures
* Useful error messages


### Installation
`pip install grasshopper-web`


### Usage

1\. Make a framework object.
```python
from grasshopper import Framework
app = Framework(settings)
```
`settings` can be any dict of settings which will be accessible from all view functions

2\. Define a view.
```python
def hello(**kwargs):
	ua = kwargs['request']['headers']['User-Agent']
	kwargs['response']['body'] = "your user agent= " + ua
	return 200
```
Writing to `kwargs['response']` defines the response to send back

`kwargs['request']` contains info about the request

`kwargs['settings']` contains the settings you passed into the Framework


Of course you can also take advantage of Python's sweet argument passing by adding them to the parameters

```python
def hello(request, response, **kwargs):
	ua = request['headers']['User-Agent']
	response['body'] = "your user agent= " + ua
	return 200
```

3\. Route a URL to the view.
`app.get('/hello/', hello)`

Routing also supports wildcard matching but you have to parse out the value in the function

For example

`app.get('/user/*/stats', user_stats)` will route `'/users/55/stats'` to `user_stats`



See the example app under /example for more details


### Running
Grasshopper is WSGI compatible so any WSGI server should work

eg.

```
from wsgiref.simple_server import make_server
server = make_server('', 8000, app)
server.serve_forever()
```
