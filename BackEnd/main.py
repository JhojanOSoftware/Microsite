import sqlite3
from BackEnd.models.Proyectos import Contactos, Proyectos, Map
from fastapi import FastAPI, HTTPException, status  

app = FastAPI()


@app.get("/dbproyects_jo/")
def crear_db():
    # Función para crear las tablas necesarias en la base de datos SQLite
    conn = sqlite3.connect('proyects01_j0.db')
    cursor = conn.cursor()
    # Tabla proyectos realizados
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS proyectos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            imagen TEXT NOT NULL,
            fecha TEXT NOT NULL,
            linkgithub TEXT NOT NULL,
            linkvideo TEXT
        )
    ''')
    # Tabla contactos
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS contactos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            telefono TEXT NOT NULL,
            email TEXT NOT NULL,
            mensaje TEXT NOT NULL
        )
    ''')
    # Tabla mapas
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS mapas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            placename TEXT NOT NULL,
            description TEXT NOT NULL,
            latitud TEXT NOT NULL,
            longitud TEXT NOT NULL,
            addresplace TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()
    return {"message": "Tablas creadas exitosamente"}, status.HTTP_201_CREATED

@app.post("/proyectos/")
def crear_proyecto(proyecto: Proyectos):
    conn = sqlite3.connect('proyects01_j0.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO proyectos (nombre, imagen, fecha, linkgithub, linkvideo) VALUES (?, ?, ?, ?, ?)
    ''', (proyecto.nombre, proyecto.imagen, proyecto.fecha, proyecto.linkgithub, proyecto.linkvideo))
    conn.commit()
    conn.close()
    return {
        "message": "Proyecto creado correctamente",
        "data": proyecto.dict()
    }
@app.get("/proyectos/")
def listar_proyectos():
    conn = sqlite3.connect('proyects01_j0.db')
    cursor = conn.cursor()
    cursor.execute('SELECT id, nombre, imagen, fecha, linkgithub, linkvideo FROM proyectos')
    proyectos = cursor.fetchall()
    conn.close()
    return {
        "message": "Lista de proyectos",
        "data": [{"id": row[0], "nombre": row[1], "imagen": row[2], "fecha": row[3], "linkgithub": row[4], "linkvideo": row[5]} for row in proyectos]
    }

@app.delete("/proyectos/{proyecto_id}")
def eliminar_proyecto(proyecto_id: int):
    conn = sqlite3.connect('proyects01_j0.db')
    cursor = conn.cursor()
    cursor.execute('DELETE FROM proyectos WHERE id = ?', (proyecto_id,))
    conn.commit()
    conn.close()
    return {
        "message": "Proyecto eliminado correctamente"
    }

@app.post("/contactos/")
def crear_contacto(contacto: Contactos):
    conn = sqlite3.connect('proyects01_j0.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO contactos (nombre, telefono, email, mensaje) VALUES (?, ?, ?, ?)
    ''', (contacto.nombre, contacto.telefono, contacto.email, contacto.mensaje))
    conn.commit()
    conn.close()
    return {
        "message": "Contacto creado correctamente",
        "data": contacto.dict()
    }
@app.get("/contactos/")
def listar_contactos():             
    conn = sqlite3.connect('proyects01_j0.db')
    cursor = conn.cursor()
    cursor.execute('SELECT id, nombre, telefono, email, mensaje FROM contactos')
    contactos = cursor.fetchall()
    conn.close()
    return {
        "message": "Lista de contactos",
        "data": [{"id": row[0], "nombre": row[1], "telefono": row[2], "email": row[3], "mensaje": row[4]} for row in contactos]
    }

@app.delete("/contactos/{contacto_id}")  
def delete_contacto(contacto_id: int):
    conn = sqlite3.connect('proyects01_j0.db')
    cursor = conn.cursor()
    cursor.execute('DELETE FROM contactos WHERE id = ?', (contacto_id,))
    conn.commit()
    conn.close()
    return {
        "message": "Contacto eliminado correctamente"
    }

@app.post("/mapas/")            
def createnode(map: Map):
    conn = sqlite3.connect('proyects01_j0.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO mapas (placename, description, latitud, longitud, addresplace) VALUES (?, ?, ?, ?, ?)
    ''', (map.placename, map.description, map.latitud, map.longitud, map.addresplace))
    conn.commit()
    conn.close()
    return {
        "message": "Lugar creado correctamente",
        "data": map.dict()
    }
@app.get("/mapas/")
def list_map():     
    conn = sqlite3.connect('proyects01_j0.db')
    cursor = conn.cursor()
    cursor.execute('SELECT id, placename, description, latitud, longitud, addresplace FROM mapas')
    mapas = cursor.fetchall()
    conn.close()
    return {
        "message": "Lista de lugares",
        "data": [{"id": row[0], "placename": row[1], "description": row[2], "latitud": row[3], "longitud": row[4], "addresplace": row[5]} for row in mapas]
    }
@app.delete("/mapas/{map_id}")
def delete_map_entry(map_id: int):
    conn = sqlite3.connect('proyects01_j0.db')
    cursor = conn.cursor()
    cursor.execute('DELETE FROM mapas WHERE id = ?', (map_id,))
    conn.commit()
    conn.close()
    return {
        "message": "Lugar eliminado correctamente"
    }