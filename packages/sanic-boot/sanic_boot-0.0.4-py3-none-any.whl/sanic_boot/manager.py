"""
@file    : __init__.py
@author  : yingHan/嬴寒
@email   : yinghan22@163.com
@create  : 2025/12/5 14:49
"""
import argparse
import os
import platform
from pathlib import Path


def sanicBootInit(__targetPath__) -> None:
    targetPath = Path(__targetPath__)
    if __targetPath__.startswith("/"):  # relative file path
        targetPath = Path.cwd() / __targetPath__
    osType = platform.system()
    currFilePath = __file__
    currDirPath = os.path.dirname(currFilePath)
    projectTemplatePath = os.path.join(currDirPath, 'projectTemplate', '*')
    from_to = {'from': projectTemplatePath, 'to': targetPath}
    if osType == "Windows":
        cmd = 'copy {from} {to}'.format(**from_to)
    elif osType == "Darwin":
        cmd = 'cp -R {from} {to}'.format(**from_to)
    else:
        cmd = 'cp -r {from} {to}'.format(**from_to)
    os.system(cmd)


view_text = '二者不能在 sanic 实例所在的文件中出现。如要在 sanic 实例中书写/创建路由，建议使用 sanic ' \
            '原生提供的装饰器等形式（即app.{get,post,route,...}）。使用 Controller 与 Views 形式创建的路由将会自动挂载到 sanic 实例/蓝图上。手动创建的路由必须手动挂载到 sanic ' \
            '实例/蓝图上。此外，Views 将比 Controller 优先挂载。'

infoWhich = {
    'Controller': f'Controller  控制器，与 Views 不同。Controller 面向类，Views 面向函数。{view_text}',
    'Views': f'Views       视图，与Controller 不同。Controller 面向类，Views 面向函数。{view_text}',
    'Resource': 'Resource    静态文件的约定目录',
    'Models': 'Models      模型文件的约定目录',
    'Tasks': 'Tasks       自动化任务的约定目录',
    'config': 'config.ini  核心配置文件。不支持自定义配置文件名称'
}


def sanicBooter() -> None:
    parser = argparse.ArgumentParser(description="sanic-boot helper")
    subParser = parser.add_subparsers(dest='command')

    initParser = subParser.add_parser("init", help='项目初始化命令')
    initParser.add_argument('dir', help='the directory to create the project in/with.')

    helpParser = subParser.add_parser('help')

    infoParser = subParser.add_parser("info", help='目录信息')
    infoParser.add_argument('target', choices=['all'] + list(infoWhich.keys()), help='help the project for sanic booter')

    args = parser.parse_args()

    match args.command:
        case 'init':
            sanicBootInit('./' if args.dir is None else args.dir)
        case 'info':
            if args.target == 'all':
                print(
                    '\n\n'.join([
                        '\n'.join([
                            f"{' ' * 4 if index != 0 else ''}{item}。" for index, item in enumerate(content.split('。'))
                            if len(item)
                        ])
                        for content in infoWhich.values()
                    ])
                )
            else:
                print(
                    '\n'.join([
                        f"{' ' * 4 if index != 0 else ''}{item}。" for index, item in enumerate(infoWhich.get(args.target).split(
                            '。')) if
                        len(item)
                    ])
                )
        case 'help':
            print(
                '\n'
                '本项目旨在降低 sanic 框架在使用中的复杂度，以 sanic 为基础进行二次开发，整体结构参考了 SpringBoot 的特点。\n\n'
                '**部分 API 可能会对性能造成影响。**\n\n'
                '_注意_：本项目仅适用于中小型项目，对于大型项目建议使用 sanic、Flask、FastAPI、Django、Spring '
                'Boot 或其他优秀框架。\n')
        case _:
            parser.print_help()
