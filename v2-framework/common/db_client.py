# common/db_client.py
import pymysql
from config.settings import Config

class DbClient:
    @classmethod
    def query_one(cls, sql):
        """执行查询，返回第一条记录（元组）"""
        conn = pymysql.connect(
            host=Config.DB_HOST,
            user=Config.DB_USER,
            password=Config.DB_PASSWORD,
            database=Config.DB_NAME,
            charset="utf8mb4"
        )
        cursor = conn.cursor()
        cursor.execute(sql)
        result = cursor.fetchone()
        cursor.close()
        conn.close()
        return result