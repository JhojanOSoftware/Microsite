import sqlite3
import traceback
from typing import List, Dict, Optional

from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware

from BackEnd.models.Proyectos import Proyectos, Contactos, Map

app = FastAPI(title="Actividad Microsite API")

# Ajusta orígenes según donde sirvas el frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:5500", "http://localhost:5500", "http://localhost:3000", "http://127.0.0.1:8000", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DB_FILE = "proyects01_j0.db"


def get_conn() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_FILE, timeout=10)
    conn.row_factory = sqlite3.Row
    return conn


def ensure_db() -> None:
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS proyectos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            description TEXT NOT NULL,
            imagen TEXT NOT NULL,
            fecha TEXT NOT NULL,
            linkgithub TEXT NOT NULL,
            linkvideo TEXT NOT NULL
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS contactos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            telefono TEXT NOT NULL,
            email TEXT NOT NULL,
            mensaje TEXT NOT NULL
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS mapas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            placename TEXT NOT NULL,
            description TEXT NOT NULL,
            latitud TEXT NOT NULL,
            longitud TEXT NOT NULL,
            addresplace TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()


@app.on_event("startup")
def startup():
    ensure_db()


@app.get("/dbproyects_jo/")
def crear_db_endpoint():
    try:
        ensure_db()
        return {"message": "Tablas creadas o verificadas correctamente"}
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error creando tablas: {e}")


@app.post("/proyectos/", status_code=status.HTTP_201_CREATED)
def crear_proyecto(proyecto: Proyectos):
    try:
        conn = get_conn()
        cur = conn.cursor()
        cur.execute(
            """
            INSERT INTO proyectos (nombre, description, imagen, fecha, linkgithub, linkvideo)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (proyecto.nombre, proyecto.description, proyecto.imagen, proyecto.fecha, proyecto.linkgithub, proyecto.linkvideo)
        )
        conn.commit()
        new_id = cur.lastrowid
        conn.close()
        return {"message": "Proyecto creado correctamente", "id": new_id, "data": proyecto.dict()}
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error creando proyecto: {e}")


@app.get("/proyectos/")
def listar_proyectos():
    try:
        conn = get_conn()
        cur = conn.cursor()
        cur.execute("SELECT id, nombre, description, imagen, fecha, linkgithub, linkvideo FROM proyectos ORDER BY id DESC")
        rows = cur.fetchall()
        conn.close()
        data = [dict(r) for r in rows]
        return {"message": "Lista de proyectos", "data": data}
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error listando proyectos: {e}")


@app.delete("/proyectos/{proyecto_id}")
def eliminar_proyecto(proyecto_id: int):
    try:
        conn = get_conn()
        cur = conn.cursor()
        cur.execute("DELETE FROM proyectos WHERE id = ?", (proyecto_id,))
        conn.commit()
        affected = cur.rowcount
        conn.close()
        if affected == 0:
            raise HTTPException(status_code=404, detail="Proyecto no encontrado")
        return {"message": "Proyecto eliminado correctamente"}
    except HTTPException:
        raise
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error eliminando proyecto: {e}")


@app.post("/contactos/", status_code=status.HTTP_201_CREATED)
def crear_contacto(contacto: Contactos):
    try:
        conn = get_conn()
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO contactos (nombre, telefono, email, mensaje) VALUES (?, ?, ?, ?)",
            (contacto.nombre, contacto.telefono, contacto.email, contacto.mensaje)
        )
        conn.commit()
        new_id = cur.lastrowid
        conn.close()
        return {"message": "Contacto creado correctamente", "id": new_id, "data": contacto.dict()}
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error creando contacto: {e}")


@app.get("/contactos/")
def listar_contactos():
    try:
        conn = get_conn()
        cur = conn.cursor()
        cur.execute("SELECT id, nombre, telefono, email, mensaje FROM contactos ORDER BY id DESC")
        rows = cur.fetchall()
        conn.close()
        data = [dict(r) for r in rows]
        return {"message": "Lista de contactos", "data": data}
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error listando contactos: {e}")


@app.delete("/contactos/{contacto_id}")
def delete_contacto(contacto_id: int):
    try:
        conn = get_conn()
        cur = conn.cursor()
        cur.execute("DELETE FROM contactos WHERE id = ?", (contacto_id,))
        conn.commit()
        affected = cur.rowcount
        conn.close()
        if affected == 0:
            raise HTTPException(status_code=404, detail="Contacto no encontrado")
        return {"message": "Contacto eliminado correctamente"}
    except HTTPException:
        raise
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error eliminando contacto: {e}")


@app.post("/mapas/", status_code=status.HTTP_201_CREATED)
def createnode(map: Map):
    try:
        conn = get_conn()
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO mapas (placename, description, latitud, longitud, addresplace) VALUES (?, ?, ?, ?, ?)",
            (map.placename, map.description, map.latitud, map.longitud, map.addresplace)
        )
        conn.commit()
        new_id = cur.lastrowid
        conn.close()
        return {"message": "Lugar creado correctamente", "id": new_id, "data": map.dict()}
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error creando lugar: {e}")


@app.get("/mapas/")
def list_map():
    try:
        conn = get_conn()
        cur = conn.cursor()
        cur.execute("SELECT id, placename, description, latitud, longitud, addresplace FROM mapas ORDER BY id DESC")
        rows = cur.fetchall()
        conn.close()
        data = [dict(r) for r in rows]
        return {"message": "Lista de lugares", "data": data}
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error listando lugares: {e}")


@app.delete("/mapas/{map_id}")
def delete_map_entry(map_id: int):
    try:
        conn = get_conn()
        cur = conn.cursor()
        cur.execute("DELETE FROM mapas WHERE id = ?", (map_id,))
        conn.commit()
        affected = cur.rowcount
        conn.close()
        if affected == 0:
            raise HTTPException(status_code=404, detail="Lugar no encontrado")
        return {"message": "Lugar eliminado correctamente"}
    except HTTPException:
        raise
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error eliminando lugar: {e}")


