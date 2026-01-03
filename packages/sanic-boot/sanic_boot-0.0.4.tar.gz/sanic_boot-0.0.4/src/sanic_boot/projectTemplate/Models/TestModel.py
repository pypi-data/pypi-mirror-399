from tortoise import Model, fields


class TestModel(Model):
    name = fields.CharField(max_length=255, required=True, description='姓名')
    age = fields.IntField(description='年龄')
    webSrc = fields.TextField(description='个人网址')
    description = fields.TextField(description='个人简介')
