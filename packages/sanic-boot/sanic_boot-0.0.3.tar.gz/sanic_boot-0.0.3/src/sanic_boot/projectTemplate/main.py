from sanic_boot import sanicBoot, Config

app = sanicBoot(__name__, docs=True)

if __name__ == '__main__':
    app.run(
        host=Config.Server.host,
        port=Config.Server.port,
        debug=Config.Server.debug,
        auto_reload=Config.Server.auto_reload,
        access_log=Config.Server.access_log,
    )
