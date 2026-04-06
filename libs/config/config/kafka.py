import json
from os import getenv
from dotenv import load_dotenv

load_dotenv()


BOOTSTRAP_SERVERS = getenv("BOOTSTRAP_SERVERS")


def VALUE_SERIALIZER(v):
    return json.dumps(v).encode("utf-8")


def VALUE_DESERIALIZER(v):
    return json.loads(v.decode("utf-8"))
