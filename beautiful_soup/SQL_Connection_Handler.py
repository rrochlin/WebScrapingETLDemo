import sqlalchemy as sal
from base_logger import logger


class SQL_Connection_Handler():
    def __init__(self) -> None:
        dialect = "postgresql"
        secrets = open("../SQL_Secrets.txt")
        username, password, host, port = [line.replace("\n", "") for line in secrets]
        database = "postgres"
        url_object = sal.engine.URL.create(dialect,
                                           username=username,
                                           password=password,
                                           host=host,
                                           port=port,
                                           database=database)
        logger.info("creating sql engine")
        self.engine = sal.create_engine(url_object)
