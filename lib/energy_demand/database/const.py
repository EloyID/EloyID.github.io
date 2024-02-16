import os

DATABASE_NAME = (
    os.environ.get("HADES_DATABASE_NAME")
    if os.environ.get("HADES_DATABASE_NAME")
    else "hades"
)
DATABASE_HOST = (
    os.environ.get("HADES_DATABASE_HOST")
    if os.environ.get("HADES_DATABASE_HOST")
    else "localhost"
)
DATABASE_USER = os.environ.get("HADES_DATABASE_USER")
DATABASE_PASSWORD = os.environ.get("HADES_DATABASE_PASSWORD")

MYSQL_DATABASE_URI = (
    f"mysql://{DATABASE_USER}:{DATABASE_PASSWORD}@{DATABASE_HOST}/{DATABASE_NAME}"
)
