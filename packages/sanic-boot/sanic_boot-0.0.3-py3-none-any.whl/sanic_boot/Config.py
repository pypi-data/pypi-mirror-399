"""
@file    : Config.py
@author  : yingHan/嬴寒
@email   : yinghan22@163.com
@create  : 2025/12/3 12:29
"""


class Config:
    class Server:
        host = "0.0.0.0"
        port = 8080
        debug = True
        auto_reload = True
        access_log = True
        resource: set[dict[str, str]] = []

    class Database:
        dbtype = "sqlite"
        host = "127.0.0.1"
        port = 3306
        path = ""
        user = ""
        password = ""
        database = ""
        generate_schemas = True
        driver = ""
        sync = False


__all__ = ["Config"]
