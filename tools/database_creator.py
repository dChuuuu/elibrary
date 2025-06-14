import asyncio
import logging
from dataclasses import dataclass
from env import POSTGRES_USER_PASSWORD, DATABASE_USER, DATABASE_USER_PASSWORD, DATABASE_NAME
import asyncpg


logger = logging.getLogger('tools.database_creator')
logger.setLevel(logging.INFO)

formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')


console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(formatter)


logger.addHandler(console_handler)


@dataclass
class BaseDatabase:
    pg_passwd: str
    db_name: str
    db_user: str
    db_user_passwd: str


class Database(BaseDatabase):

    async def create_database(self):

        logger.info('Подключение к рут-базе данных...')

        try:
            connection = await asyncpg.connect(host='localhost', port='5432', user='postgres',
                                  password=self.pg_passwd, database='postgres')
            logger.info('Подключение успешно!')
        except Exception as e:
            logger.info(f'Ошибка подключения: {e}')
            return None

        logger.info('Создание рут-пользователя...')
        try:
            await connection.fetch(f"""CREATE USER {self.db_user} WITH PASSWORD '{self.db_user_passwd}';""")
            await connection.fetch(f"""ALTER USER {self.db_user} WITH SUPERUSER;""")
            logger.info('Пользователь создан успешно!')

        except Exception as error:
            logger.info('Рут-пользователь уже создан')

        logger.info('Создание базы данных...')
        try:
            await connection.fetch(f"""CREATE DATABASE {self.db_name};""")
        except Exception as error:
            logger.info('База данных уже создана')
        await connection.close()
        logger.info('Процесс завершен')


async def main():
    database_task = Database(POSTGRES_USER_PASSWORD, DATABASE_NAME,
                             DATABASE_USER, DATABASE_USER_PASSWORD).create_database()

    await asyncio.create_task(database_task)


if __name__ == '__main__':
    asyncio.run(main())
