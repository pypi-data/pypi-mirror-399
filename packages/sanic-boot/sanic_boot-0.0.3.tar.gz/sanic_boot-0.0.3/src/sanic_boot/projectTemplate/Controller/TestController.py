from sanic import response, Request, HTTPResponse
from sanic_boot.core import Controller, GetMapping, RequestMapping, RequestMethod


@Controller(uri='/')
class IndexController:

    @GetMapping('/get')
    def get(self, request: Request) -> HTTPResponse:
        return response.json({'status': 200})


@Controller
class TestController:
    @RequestMapping('/logout', RequestMethod.GET)
    async def logout(self, request: Request) -> HTTPResponse:
        return response.json({'status': 200})
