"""
@file    : __init__.py
@author  : yingHan/嬴寒
@email   : yinghan22@163.com
@create  : 2025/12/5 14:49
"""
import os
from configparser import ConfigParser
from importlib import import_module
from pathlib import Path
from types import SimpleNamespace, ModuleType
from typing import Iterator

try:
    import sanic
    from sanic import Sanic, Blueprint
    from tortoise import Model

    from tortoise.contrib.sanic import register_tortoise
except ModuleNotFoundError:
    raise EnvironmentError('Please install sanic : uv add sanic tortoise-orm')

from sanic_boot.Config import Config
from .core import *

separator = os.sep

projectRootDir = Path.cwd()


def initConfiguration(configFilePath) -> None:
    configParser = ConfigParser()
    configParser.read(configFilePath, encoding="utf-8")

    sectionFieldTypeActionMapping: dict[str, Callable] = {
        "int": configParser.getint,
        "float": configParser.getfloat,
        "str": configParser.get,
        "bool": configParser.getboolean,
        "list": configParser.get,
    }

    for section in configParser.sections():
        # print(section)
        configSectionName = f"{section[0].upper()}{section[1:]}"

        configSection = getattr(Config, configSectionName)
        fieldNameList: list[str] = configParser.options(section)

        for fieldName in fieldNameList:
            field = getattr(configSection, fieldName)
            fieldType = type(field)
            value: int | float | str | bool | None | list = None
            get = sectionFieldTypeActionMapping.get(fieldType.__name__)
            value = get(section, fieldName)

            if fieldName in ["resource"]:
                resourceList: list[str] = [value]
                for splitter in [",", ":", ";", "，", "：", "；"]:
                    result: list[str] = []
                    for item in resourceList:
                        result += item.split(splitter)
                    resourceList = result
                value = [
                    {
                        "router": item.strip().split("=")[0].strip(),
                        "filePath": item.strip().split("=")[1].strip(),
                    }
                    for item in resourceList
                    if item.strip() != ""
                ]

            setattr(configSection, fieldName, value)


def loadModels():
    moduleEntryPath = Path("Models/__init__.py")
    if not moduleEntryPath.exists():
        with open(moduleEntryPath, mode="w+"):
            pass
    moduleEntry: ModuleType = import_module(f"Models.__init__")
    # print(moduleEntry)
    ModelsRootDir = projectRootDir / "Models"
    fileList: Iterator[Path] = ModelsRootDir.rglob("**/*.py")
    for fileName in fileList:
        moduleName: str = str(fileName).split(separator)[-1][:-3]
        module: ModuleType = import_module(f"Models.{moduleName}")
        if moduleName == "__init__":
            continue
        else:
            memberNameList: list[str] = dir(module)
            for memberName in memberNameList:
                member: Any = getattr(module, memberName)
                if inspect.isclass(member) and issubclass(member, Model) and member is not Model:
                    if memberName not in dir(moduleEntry):
                        setattr(moduleEntry, memberName, member)
                    else:
                        raise Exception("Model name conflict")
    return moduleEntry


def initDatabase(app: Sanic):
    models = loadModels()

    url: str = ""
    match Config.Database.dbtype:
        case "sqlite":
            url = "sqlite://{}".format(Config.Database.path)
        case "postgres":
            protocol: str = "asyncpg" if Config.Database.sync else "psycopg"
            url = "{}://{}:{}@{}:{}/{}".format(
                protocol,
                Config.Database.user,
                Config.Database.password,
                Config.Database.host,
                Config.Database.port,
                Config.Database.database,
            )
        case "mysql":
            url = "mysql://{}:{}@{}:{}/{}".format(
                Config.Database.user,
                Config.Database.password,
                Config.Database.host,
                Config.Database.port,
                Config.Database.database,
            )
        case "mssql":
            url = "mssql://{}:{}@{}:{}/{}{}".format(
                Config.Database.user,
                Config.Database.password,
                Config.Database.host,
                Config.Database.port,
                Config.Database.database,
                f"?driver={Config.Database.driver}" if Config.Database.driver else "",
            )
    register_tortoise(app=app, db_url=url, modules={"models": [models]}, generate_schemas=Config.Database.generate_schemas)


def collectViewRouter(app: Sanic):
    viewRootDir = projectRootDir / "Views"
    fileList: Iterator[Path] = viewRootDir.rglob("**/*.py")
    for fileName in fileList:
        # print(fileName)
        moduleName: str = str(fileName).split(separator)[-1][:-3]
        module: ModuleType = import_module(f"Views.{moduleName}")
        for memberName in dir(module):
            member = getattr(module, memberName)
            if not hasattr(member, "__isView__"):
                continue
            # else
            router = getattr(member, "__viewRouter__")
            app.add_route(**router)
    # app.add_route(handler, '/test', methods=["POST", "PUT"])


def collectController(app: Sanic):
    controllerRootDir = projectRootDir / "Controller"
    fileList: Iterator[Path] = controllerRootDir.rglob("**/*.py")
    blueprintList = []
    for fileName in fileList:
        # print(fileName)
        moduleName: str = str(fileName).split(separator)[-1][:-3]
        module: ModuleType = import_module(f"Controller.{moduleName}")
        for memberName in dir(module):
            member = getattr(module, memberName)
            if not hasattr(member, "__controller__"):
                continue
            # else
            blueprint = Blueprint(member.__name__, url_prefix=getattr(member, "__controller__"))
            for attrName in dir(member):
                attr = getattr(member, attrName)
                if not hasattr(attr, "__viewRouter__"):
                    continue
                # else:
                routerInfo: dict = getattr(attr, "__viewRouter__")
                if "as_view" not in routerInfo["handler"].__qualname__:
                    if not hasattr(member, "staticSelf"):
                        setattr(member, "staticSelf", member())
                    staticSelf = getattr(member, "staticSelf")
                    routerInfo["handler"] = getattr(staticSelf, attr.__name__)
                # routerInfo["handler"] = staticmethod(routerInfo["handler"])
                blueprint.add_route(**routerInfo)
            blueprintList.append(blueprint)
    app.blueprint(blueprint=blueprintList)
    return app


def collectTask(app: Sanic):
    taskRootDir = projectRootDir / "Tasks"
    fileList: Iterator[Path] = taskRootDir.rglob("**/*.py")
    for fileName in fileList:
        # print(fileName)
        moduleName: str = str(fileName).split(separator)[-1][:-3]
        module: ModuleType = import_module(f"Tasks.{moduleName}")
        for memberName in dir(module):
            member = getattr(module, memberName)
            if not hasattr(member, "__isTask__"):
                continue
            # else
            conf = getattr(member, "__task__")
            app.add_task(member, name=conf["name"])
    return app


cors_default_option = {
    "CORS_ALLOW_HEADERS": "*",
    "CORS_ALWAYS_SEND": True,
    "CORS_AUTOMATIC_OPTIONS": True,
    "CORS_EXPOSE_HEADERS": "*",
    "CORS_MAX_AGE": 0,
    "CORS_METHODS": "*",
    "CORS_ORIGINS": "*",
    "CORS_SEND_WILDCARD": False,
    "CORS_SUPPORTS_CREDENTIALS": False,
    "CORS_VARY_HEADER": True,
}

docs_default_option = {
    "OAS_IGNORE_HEAD": True,
    "OAS_IGNORE_OPTIONS": True,
    "OAS_PATH_TO_REDOC_HTML": None,
    "OAS_PATH_TO_SWAGGER_HTML": None,
    "OAS_UI_DEFAULT": "redoc",
    "OAS_UI_REDOC": False,
    "OAS_UI_SWAGGER": True,
    "OAS_URI_TO_CONFIG": "/swagger-config",
    "OAS_URI_TO_JSON": "/openapi.json",
    "OAS_URI_TO_REDOC": "/redoc",
    "OAS_URI_TO_SWAGGER": "/swagger",
    "OAS_URL_PREFIX": "/docs",
}


def sanicBoot(
        name: str,
        router: str | None = None,
        *,
        blueprint: Blueprint | list[Blueprint] | None = None,
        docs: bool = False,
        docsConfig=None,
        corsConfig=None,
) -> Sanic[sanic.Config, SimpleNamespace]:
    if corsConfig is None:
        corsConfig = cors_default_option
    if docsConfig is None:
        docsConfig = docs_default_option
    app = Sanic(name, router=router)

    configFilePath: Path = projectRootDir / "config.ini"

    initConfiguration(configFilePath)

    initDatabase(app=app)

    collectViewRouter(app)
    collectController(app)

    for item in Config.Server.resource:
        app.static(item["router"], item["filePath"])
    if corsConfig:
        app.update_config(cors_default_option)
    if docsConfig:
        app.update_config(docs_default_option)

    collectTask(app)

    return app


if __name__ == "__main__":
    projectRootDir: Path = projectRootDir / "projectTemplate"
    # sanicBoot('sanic')
    # loadModels()
    # pass

    app = sanicBoot(__name__)
    app.run(debug=True, host="0.0.0.0", port=5000)
