![sanic Framework boot | sanic-boot](sanic-framework-boot-logo-400x93.png)

# sanic-boot

sanic-boot 基于 Sanic 框架，为开发者提供与 Spring Boot 类似的装饰器，便于路由系统、模型类的自动装配与配置。

## Sanic | Build fast. Run fast.

Sanic is a Python 3.9+ web server and web framework that's written to go fast. It allows the usage of the `async/await` syntax added in
Python
3.5, which makes your code non-blocking and speedy.

## 注意

本框架没有对原生的 `sanic` 框架造成任何侵入性的修改，但由于模型（Models）、路由（Routers）、任务（Task）等自动加载实现机制较为笨拙，可能会对 `sanic`
的网络请求造成不可预估的影响。

## TODO List

+ [x] 自动装配基础路由
+ [x] 自动装配类视图路由
+ [x] 自动装配 Background Task
+ [x] 自动装配模型类
+ [x] 文档
+ [x] Websocket
+ [x] 流式传输（Streaming）
+ [ ] 为 Controller 注入 CRUD 操作
+ [ ] 封装 APScheduler 定时任务框架

## 安装

```bash
# 使用 pip
pip install sanic-boot

# 使用uv
uv add sanic-boot
```

### 可能的依赖

```bash
# 使用 pip
pip install sanic sanic-ext tortoise-orm
# 或
pip install sanic[ext] tortoise-orm[asyncpg|psycopg|asyncmy|asyncodbc]

# 使用 uv
uv add ...
```

sanic-ext 提供 docs、cors 等；
tortoise-orm 提供 ORM 等。

## Hello World Example

```python
from sanic_boot import sanicBoot
import sanic

app = sanicBoot(__name__)


# 使用 sanic 自带的装饰器仍然有效
@app.get("/")
def index(request):
    return sanic.response.text("hello")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8088, debug=True, auto_reload=True)

```

### 1. Create NORMAL route by common function (which can be with `async`)

```python
from sanic import Request, text
from sanic_boot import GetMapping


# 面向函数
@GetMapping('/index')
async def index(request: Request):
    return text('Hello')
```

### 2. Create Router View from class, which just collect the route -- A simple method instead of blueprint

```python
from sanic import Request, text, json
from sanic_boot import Controller, GetMapping, RequestMapping


# 面向类
@Controller('/person')
class PersonController:
    # 使用 RequestMapping 装饰器后，若发现目标是类且不是 HTTPMethodView 的子类，则会在继承链中添加 HTTPMethodView 类。
    # （*注意*：此举可能会造成多继承冲突！！！）
    @RequestMapping('/login')
    class Login:
        async def get(self, request: Request):
            return text('the route is /person/login')

    # 除视图外，还可以使用普通方法构造路由
    @GetMapping('/logout')
    async def logout(self, request: Request):
        return json({
            'code': 200,
            'data': '退出登录'
        })
```

### 3. Create Task by decorator `Task`, which is allowed to get a parameter named `name` or

`taskName`. If there is no parameter has, the value `None` will be the default value assigned to argument `name`。

```python
import asyncio
from sanic import Sanic
from sanic_boot import Task


@Task(name='')  # name 或 taskName 默认为 None
async def gen(app: Sanic):
    while True:
        print([item for item in range(10)])
        await asyncio.sleep(5000)
```

## Decorator Description

+ `@Controller (uri : str = '')`
  > 装饰器 `Controller` 意在收集目标注解对象内部注册的路由，是 `sanic` 框架中 `blueprint` 蓝图系统的自动化实现。
  >
  > sanic 官方网站中提供了自动收集 blueprint 的辅助文件，能够帮助开发者给予蓝图系统快速构建路由系统。而装饰器 `Controller` 则延伸了官方方案，参考
  `Spring Boot` 装饰器思路，提供能够相对完备的路由系统自动组装方案。
  >
  > 装饰器 `Controller`允许不携带任何参数，此时将自动分配路由，分配的路由与目标注解的类名有关，类名推荐的格式为
  `^[A-Z][A-Za-z0-9]*Controller$`
  ，（即大写字母开头的有意义单词，并以单词 Controller
  > 结尾），分配所得路由为全小写且不含 `Controller`。如 `TestController` 的路由为 `test`，`TestTest2Controller` 的路由为 `test-test2`
  >
  > _注意_: 若最终注册的路由存在重复将会造成**路由冲突**，此外，若注册的函数名在相同层级上存在重复，也会造成路由系统收集异常。故建议开发者在不同业务中为路由句柄（handler）赋予不同的名称

+ `@RequestMapping(uri : str, methods: list[RequestMethod] | RequestMethod | None = None)`
  > 使用 `RequestMapping` 时若注解对象是一个视图类，则第二个参数可缺省，`sanic` 内部的路由系统将会根据视图类的方法自动分配路由方法。装饰器
  `RequestMapping` 是 `sanic` 框架中类视图注册方法 `app.add_route (Class.as_view(), ...)` 的自动化实现。

+ `@[Get|Post|Head|Put|Delete|Patch|Options]Mapping(uri : str)`
  > `@GetMapping (uri : str)` 等装饰器是 `@RequestMapping ('/login', RequestMethod.GET)`
  > 的简便写法。需要注意的是这些简便写法尽量不要应用在视图类上。但基于实际的代码逻辑实现而言，即使对视图类上进行应用，也不会造成任何不可预计的后果。

+ `@Task(name : str = None)`
  > 在 Tasks 目录下注册任务事件。目前尚未想好如何以最佳的形式将 APScheduler 封装进去，故开发者可根据自己需要进行封装。

[//]: # ()

[//]: # (## 目前已对 sanic 框架中下列勾选的内容做了二次封装)

[//]: # ()

[//]: # (+ [x] static files（简单映射）)

[//]: # (+ [x] 基础路由)

[//]: # (+ [x] Websocket)

[//]: # (+ [ ] 路由上下文)

[//]: # (+ [ ] 监听器)

[//]: # (+ [ ] ASGI 模式)

[//]: # (+ [ ] 中间件)

[//]: # (+ [ ] 头处理)

[//]: # (+ [x] 后台任务（Background tasks）)

[//]: # (+ [x] 类视图（Class Based View）)

[//]: # (+ [x] 路径参数)

[//]: # (+ [ ] 代理配置)

[//]: # (+ [ ] 流式传输（Streaming）)

[//]: # (+ [ ] 路由系统中的版本控制)

[//]: # (+ [ ] 信号)

[//]: # (+ [ ] 命令（New in v24.12）)

[//]: # (+ [x] 蓝图（Blueprints）（基础封装）)

[//]: # (+ [ ] 异常)

[//]: # (+ [ ] 日志)

[//]: # (+ [ ] 测试)

[//]: # (+ [x] 配置)

[//]: # (+ [ ] 自动加载/重载)

[//]: # (+ [ ] TLS/SSL/HTTPS)

[//]: # (+ [ ] 运行 Sanic)

[//]: # (+ [ ] 检查器（Inspector）)

[//]: # (+ [ ] 认证（Authentication）)

[//]: # (+ [x] 自动发现)

[//]: # (+ [ ] 跨域资源共享（CORS）)

[//]: # (+ [x] ORM &#40;基于 tortoise-orm&#41;)

[//]: # (+ [ ] 静态重定向（"Static" Redirects）)

[//]: # (+ [x] 文档)

[//]: # (+ [ ] 安全方案)

[//]: # (+ [ ] 便携性（Convenience）)

[//]: # (+ [ ] Jinja 模板)

[//]: # (+ [ ] 依赖注入)

[//]: # (+ [ ] 验证（Validation）)