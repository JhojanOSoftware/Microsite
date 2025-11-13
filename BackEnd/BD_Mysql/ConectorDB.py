import sqlite3
import pymysql
from tqdm import tqdm

class ConectorDB:
    def __init__(self):
        self.mysql_conf = {
            "host": "localhost",
            "user": "jhojan",
            "password": "Myestrell@1929*",
            "database": "ProyectoJ0",
            "charset": "utf8mb4",
            "cursorclass": pymysql.cursors.DictCursor
        }

    def baseConnect(self):
            return pymysql.connect(**self.mysql_conf)

    def migration(self):
        SQLITE_DB = "Backend/proyectos01_j0.db"
        MYSQL_CONFIG = {
        "host": "localhost",
        "user": "jhojan",
        "password": "Myestrell@1929*",
        "database": "ProyectoJ0",
        "charset": "utf8mb4",
        "cursorclass": pymysql.cursors.DictCursor}    
        sqlite_conn = sqlite3.connect(SQLITE_DB)
        sqlite_conn.row_factory = sqlite3.Row
        mysql_conn = pymysql.connect(**MYSQL_CONFIG)

        sqlite_cur = sqlite_conn.cursor()
        mysql_cur = mysql_conn.cursor()

        sqlite_cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tablas = [t[0] for t in sqlite_cur.fetchall() if t[0] != 'sqlite_sequence']
        for tabla in tablas:
            print(f"Migrando tabla: {tabla}")

            sqlite_cur.execute(f"SELECT * FROM {tabla}")
            filas = sqlite_cur.fetchall()
            if not filas:
                print("  (tabla vacía)")
            continue

        #Obt valid c  
        mysql_cur.execute(f"DESCRIBE {tabla}")
        columnas_mysql = [col["Field"] for col in mysql_cur.fetchall()]

        # filter ambas db in tables 
        columnas_comunes = [c for c in filas[0].keys() if c in columnas_mysql]
        columnas_str = ", ".join(columnas_comunes)
        placeholders = ", ".join(["%s"] * len(columnas_comunes))
        insert_sql = f"INSERT INTO {tabla} ({columnas_str}) VALUES ({placeholders})"

        for fila in tqdm(filas, desc=f"   Insertando {tabla}", ncols=80):
            valores = [fila[c] for c in columnas_comunes]
            try:
                mysql_cur.execute(insert_sql, valores)
            except Exception as e:
                print(f" Error en fila: {dict(fila)}")
                print(f"   Motivo: {e}")

        mysql_conn.commit()
        print("\n Migración de data completada .")

        sqlite_conn.close()
        mysql_conn.close()
