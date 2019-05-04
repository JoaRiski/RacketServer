from aiohttp import web


class RacketServer(web.Application):

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.cache = 0

	async def handle(self, request):
	    name = request.match_info.get('name', "Anonymous")
	    text = f"Hello, {name}. This is request number {self.cache}"
	    self.cache += 1
	    return web.Response(text=text)

app = RacketServer()
app.add_routes([web.get('/', app.handle),
                web.get('/{name}', app.handle)])

web.run_app(app)
