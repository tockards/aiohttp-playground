import asyncio
import json
from aiohttp import web
from aiohttp.web import Application, Response
from aiohttp_sse import sse_response
from aiohttp_jinja2 import setup, template
import jinja2
from pathlib import Path

path = Path(__file__).parent


@template("index.html")
async def index(request):
    return {}


async def message(request):
    app = request.app
    data = await request.post()

    for queue in app["channels"]:
        payload = json.dumps(dict(data))
        await queue.put(payload)
    return Response()


async def subscribe(request):
    async with sse_response(request) as response:
        app = request.app
        queue = asyncio.Queue()
        print("Someone joined.")
        app["channels"].add(queue)
        try:
            while not response.task.done():
                payload = await queue.get()
                await response.send(payload)
                queue.task_done()
        finally:
            app["channels"].remove(queue)
            print("Someone left.")
    return response


app = web.Application()
app["channels"] = set()
setup(app, loader=jinja2.FileSystemLoader(str(path / "chat")))

app.router.add_route("GET", "/", index)
app.router.add_route("POST", "/everyone", message)
app.router.add_route("GET", "/subscribe", subscribe)
web.run_app(app, host="0.0.0.0", port=8080)
