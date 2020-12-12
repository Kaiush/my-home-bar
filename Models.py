from peewee import *

database = SqliteDatabase('site.db')

class UnknownField(object):
    def __init__(self, *_, **__):
        pass

class BaseModel(Model):
    class Meta:
        database = database

class Users(BaseModel):
    username = TextField(unique=True)
    password = TextField()
    name = TextField()
    email = TextField(unique=True)
    birthday = DateField()
    level = IntegerField()

    class Meta:
        table_name = 'users'

class Alcohols(BaseModel):
    name = TextField()
    abv = IntegerField()
    bottle_volume = IntegerField()
    ##image_file = TextField(default='default.jpg')

    class Meta:
        table_name = 'alcohols'

class Cocktails(BaseModel):
    name = TextField()
    abv = IntegerField()
    description = TextField()
    #image_file = TextField(default='default.jpg')

    class Meta:
        table_name = 'cocktails'

class Shelfs(BaseModel):
    user_id = ForeignKeyField(Users)
    alc_id = ForeignKeyField(Alcohols)
    bottles = IntegerField()

    class Meta:
        table_name = 'shelfs'
        primary_key = CompositeKey('user_id', 'alc_id')


class Recipes(BaseModel):
    cocktail_id = ForeignKeyField(Cocktails)
    alc_id = ForeignKeyField(Alcohols)

    class Meta:
        primary_key = CompositeKey('cocktail_id', 'alc_id')
        table_name = 'recipes'

TABLES = [Users, Alcohols, Cocktails, Shelfs, Recipes]

database.create_tables(TABLES, safe=True)


# def get_table_class(table_name):
#     name = table_name.title()
#     tables = (t for t in TABLES if T.name == name)


# def insert_parsed_json(db, parsed_json, table_name):
#     to_insert = to_peewee_compatible(parsed_json)
#     table = get_table_class(table)
#     table.insert
