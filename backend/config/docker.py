from configurations import values

from .common import Common


class Docker(Common):
    DATABASES = values.DatabaseURLValue('postgresql://postgres:postgres@db/postgres',
                                        environ_name="DJANGO_DATABASE_URL")


class Test(Common):
    pass
