"""Example originally adapted from https://github.com/aio-libs/aiohttp-sse
"""
import asyncio
from aiohttp import web
from aiohttp.web import Response
from aiohttp_sse import sse_response
from datetime import datetime

async def hello(request):
    name = request.query.get('name')
    async with sse_response(request) as resp:
        while True:
            data = 'Server Time : {} - {}'.format(datetime.now(), name)
            await resp.send(data)
            await asyncio.sleep(1)
    return resp

async def index(request):
    d = """
        <html>
        <body>
            <script>
                var urlParams = new URLSearchParams(window.location.search);
                name = urlParams.get('name')
                var evtSource = new EventSource("/hello?name="+name);
                evtSource.onmessage = function(e) {
                    document.getElementById('response').innerText = e.data
                }
            </script>
            <h1>Response from server:</h1>
            <div id="response"></div>
        </body>
    </html>
    """
    return Response(text=d, content_type='text/html')


app = web.Application()
app.router.add_route('GET', '/hello', hello)
app.router.add_route('GET', '/', index)
web.run_app(app, host='127.0.0.1', port=8080)