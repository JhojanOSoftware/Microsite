import sqlite3
import traceback
from xmlrpc import client
from fastapi.responses import JSONResponse
from fastapi import FastAPI, HTTPException, status, Form, Request, Query,Body
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter
from slowapi.util import get_remote_address
from openai  import OpenAI 
from BackEnd.models.Proyectos import Proyectos, Contactos, Map ,Coffee
limiter = Limiter(key_func=get_remote_address)
from fastapi.staticfiles import StaticFiles
import os



client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key="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",
    default_headers={
        "HTTP-Referer": "http://localhost:8000",
        "X-Title": "Actividad Microsite API",
        "Authorization": f"Bearer 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"
    }
)

# Inicializar la app de FastAPI
app = FastAPI(title="Actividad Microsite API")


# Aplicar el limiter a la app (opcional, para tenerlo disponible globalmente)
app.state.limiter = limiter

# 🔹 Ruta absoluta a tu carpeta de imágenes
images_path = os.path.join(os.getcwd(), "Frontend", "Images")

# 🔹 Montar la carpeta como estático
app.mount("/images", StaticFiles(directory=images_path), name="images")
# Ajusta orígenes según donde sirvas el frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:5500", "http://localhost:5500", "http://localhost:3000", "http://127.0.0.1:8000", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DB_FILE = "Backend/proyects01_j0.db"


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
    cur.execute("""
        CREATE TABLE IF NOT EXISTS coffee (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            coffee_type TEXT NOT NULL,
            coffe_image INTEGER NOT NULL,
            description TEXT NOT NULL,
            video TEXT NOT NULL
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
        cur.execute("SELECT id, placename, description, latitud, longitud, addresplace,score FROM mapas ORDER BY id DESC")
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
    
    
    


@app.post("/chat")
async def obtener_significado(message: str = Body(..., embed=True)):
    try:
        # Aquí haces la llamada a tu modelo IA
        significado = f"Comidas típicas recomendadas en {message}: Ajiaco, Bandeja Paisa, Tamal."

        return JSONResponse(content={
            "pregunta": message,
            "significado": significado
        })
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

    
@app.get("/coffee/")
def list_coffee():
    try:
        conn = get_conn()
        cur = conn.cursor()
        cur.execute("SELECT id, coffee_type, coffe_image, description, video FROM coffee ORDER BY id DESC")
        rows = cur.fetchall()
        conn.close()
        data = [dict(r) for r in rows]
        return {"message": "Lista de lugares", "data": data}
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error listando lugares: {e}")
    
@app.post("/coffee/", status_code=status.HTTP_201_CREATED)
def create_coffee(coffee: Coffee):
    try:
        conn = get_conn()
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO coffee (coffee_type, coffe_image, description, video) VALUES (?, ?, ?, ?)",
            (coffee.coffee_type, coffee.coffee_image, coffee.description, coffee.video)
        )
        conn.commit()
        new_id = cur.lastrowid
        conn.close()
        return {"message": "Café creado correctamente", "id": new_id, "data": coffee.dict()}
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error creando café: {e}")
@app.delete("/coffee/{coffee_id}")
def delete_coffee(coffee_id: int):          
    try:
        conn = get_conn()
        cur = conn.cursor()
        cur.execute("DELETE FROM coffee WHERE id = ?", (coffee_id,))
        conn.commit()
        affected = cur.rowcount
        conn.close()
        if affected == 0:
            raise HTTPException(status_code=404, detail="Café no encontrado")
        return {"message": "Café eliminado correctamente"}
    except HTTPException:
        raise
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error eliminando café: {e}")