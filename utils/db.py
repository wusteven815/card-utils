from aiofiles import open as aopen
from orjson import loads
from ujson import dumps
from aiosqlite import connect


# Internal sort
def _sort(item):
    if type(item) == list:
        return sorted(list)
    elif type(item) == dict:
        return {key: item[key] for key in sorted(item)}
    else:
        return item


# Read from jsons file
def read_json(file, key=None):
    with open(f"data/jsons/{file}.json", "r") as json_file:
        if key:
            return loads(json_file.read())[key]
        else:
            return loads(json_file.read())


# Async read from jsons file
async def aread_json(file, key=None):
    async with aopen(f"data/jsons/{file}.json", "r") as json_file:
        if key:
            return loads(await json_file.read())[key]
        else:
            return loads(await json_file.read())


# Write to jsons file
def write_json(file, item, sort=False):
    if sort:
        item = _sort(item)
    with open(f"data/jsons/{file}.json", "w") as json_file:
        json_file.write(dumps(item, indent=2, escape_forward_slashes=False))


# Async write to jsons file
async def awrite_json(file, item, sort=False):
    if sort:
        item = _sort(item)
    async with aopen(f"data/jsons/{file}.json", "w") as json_file:
        await json_file.write(dumps(item, indent=2, escape_forward_slashes=False))


# Write key-value pairs to jsons file
def write_value_json(file, **kwargs):
    data = read_json(file)
    for kwarg in kwargs:
        data[kwarg] = kwargs[kwarg]
    write_json(file, data)


# Async write key-value pairs to jsons file
async def awrite_value_json(file, **kwargs):
    data = await aread_json(file)
    for kwarg in kwargs:
        data[kwarg] = kwargs[kwarg]
    await awrite_json(file, data)


# Async SQLite3
class SQLite3:

    def __init__(self):

        self.made_changes = False
        self.db = None

    async def connect(self, file):

        self.db = await connect(f"data/sqlite3s/{file}.sqlite3")

    async def execute(self, command, fetch=None, made_changes=False):

        async with self.db.execute(" ".join(command.split())) as cursor:
            self.made_changes = made_changes
            if fetch is None:
                return_value = 0
            elif fetch == "all":
                return_value = await cursor.fetchall()
            elif fetch == "one":
                return_value = await cursor.fetchone()

        return return_value

    async def commit(self):

        if self.made_changes:
            await self.db.commit()
            self.made_changes = False

    async def close(self):

        await self.db.close()

    async def del_key(self, table, primary_key):

        await self.execute(f"DELETE FROM {table} WHERE id = {primary_key}", made_changes=True)

    async def get_key(self, table, primary_key):

        return await self.execute(f"SELECT * FROM {table} WHERE id = {primary_key}", fetch="one")

    async def set_key(self, table, primary_key, **kwargs):

        keys = f"id, {', '.join(kwargs.keys())}"
        values = f"{primary_key}, " + ', '.join(str(x) for x in kwargs.values())
        await self.execute(f"INSERT OR REPLACE INTO {table} ({keys}) VALUES ({values})", made_changes=True)
