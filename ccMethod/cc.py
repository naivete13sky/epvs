import psycopg2
from psycopg2 import sql
con = psycopg2.connect(dbname='postgres',user='postgres', host='127.0.0.1',password='cc')
con.autocommit = True #连接必须处于自动提交模式
cur = con.cursor()
# sql.SQL and sql.Identifier are needed to avoid SQL injection attacks.
cur.execute(sql.SQL('CREATE DATABASE {};').format(sql.Identifier('epdms')))

