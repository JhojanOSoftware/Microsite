import sqlite3
import traceback
from xmlrpc import client
import pymysql
from fastapi.responses import JSONResponse
from fastapi import FastAPI, HTTPException, status, Form, Request, Query,Body
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter
from slowapi.util import get_remote_address
from openai  import OpenAI 
from BackEnd.models.Proyectos import Proyectos, Contactos, Map ,Coffee,Exp
limiter = Limiter(key_func=get_remote_address)
from fastapi.staticfiles import StaticFiles
import os



client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key="key",
    default_headers={
        "HTTP-Referer": "http://localhost:8000",
        "X-Title": "Actividad Microsite API",
        "Authorization": f"Bearer key"
    }
)

# Inicializar la app de FastAPI
app = FastAPI(title="Actividad Microsite API")

def baseConnect():
    return pymysql.connect(
        host='localhost',
        user='jhojan',
        password='Myestrell@1929*',
        database='ProyectoJ0',
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor
    )
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



def ensure_db() -> None:
    conex = baseConnect()
    cursor = conex.cursor()


    cursor.execute(

"""
        CREATE TABLE IF NOT EXISTS proyectos (
            id INTEGER PRIMARY KEY AUTO_INCREMENT,
            nombre TEXT NOT NULL,
            description TEXT NOT NULL,
            imagen TEXT NOT NULL,
            fecha TEXT NOT NULL,
            linkgithub TEXT NOT NULL,
            linkvideo TEXT NOT NULL
        )
    """)
    cursor.execute(

"""
        CREATE TABLE IF NOT EXISTS contactos (
            id INTEGER PRIMARY KEY AUTO_INCREMENT,
            nombre TEXT NOT NULL,
            telefono TEXT NOT NULL,
            email TEXT NOT NULL,
            mensaje TEXT NOT NULL
        )
    """)
    cursor.execute(

"""
        CREATE TABLE IF NOT EXISTS mapas (
            id INTEGER PRIMARY KEY AUTO_INCREMENT,
            placename TEXT NOT NULL,
            description TEXT NOT NULL,
            latitud TEXT NOT NULL,
            longitud TEXT NOT NULL,
            addresplace TEXT NOT NULL,
            score INTEGER NULL
        )
    """)
    cursor.execute(

"""
        CREATE TABLE IF NOT EXISTS coffee (
            id INTEGER PRIMARY KEY AUTO_INCREMENT,
            coffee_type TEXT NOT NULL,
            coffe_image TEXT NULL,
            description TEXT NOT NULL,
            video TEXT NOT NULL
        )
    """)
    conex.commit()
    conex.close()



@app.get("/index.html")
def root():
    inpath = os.path.join("/index.html")
    with open(inpath, 'r', encoding='utf-8') as file:
        content = file.read()
    return JSONResponse(content=content)

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
        conex = baseConnect()
        cursor = conex.cursor()
        cursor.execute(
            """
            INSERT INTO proyectos (nombre, description, imagen, fecha, linkgithub, linkvideo)
            VALUES (%s, %s, %s, %s, %s, %s)
            """,
            (proyecto.nombre, proyecto.description, proyecto.imagen, proyecto.fecha, proyecto.linkgithub, proyecto.linkvideo)
        )
        conex.commit()
        new_id = cursor.lastrowid
        conex.close()
        return {"message": "Proyecto creado correctamente", "id": new_id, "data": proyecto.dict()}
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error creando proyecto: {e}")


@app.get("/proyectos/")
def listar_proyectos():
    try:
        conex = baseConnect()
        cursor = conex.cursor()
        cursor.execute("SELECT id, nombre, description, imagen, fecha, linkgithub, linkvideo FROM proyectos ORDER BY id DESC")
        rows = cursor.fetchall()
        conex.close()
        data = [dict(r) for r in rows]
        return {"message": "Lista de proyectos", "data": data}
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error listando proyectos: {e}")

@app.delete("/proyectos/{proyecto_id}")
def eliminar_proyecto(proyecto_id: int):
    try:
        conex = baseConnect()
        cursor = conex.cursor()
        cursor.execute("DELETE FROM proyectos WHERE id = %s", (proyecto_id,))
        conex.commit()
        affected = cursor.rowcount
        conex.close()
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
        conex = baseConnect()
        cursor = conex.cursor()
        cursor.execute(
            "INSERT INTO contactos (nombre, telefono, email, mensaje) VALUES (%s, %s, %s, %s)",
            (contacto.nombre, contacto.telefono, contacto.email, contacto.mensaje)
        )
        conex.commit()
        new_id = cursor.lastrowid
        conex.close()
        return {"message": "Contacto creado correctamente", "id": new_id, "data": contacto.dict()}
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error creando contacto: {e}")


@app.get("/contactos/")
def listar_contactos():
    try:
        conex = baseConnect()
        cursor = conex.cursor()
        cursor.execute("SELECT id, nombre, telefono, email, mensaje FROM contactos ORDER BY id DESC")
        rows = cursor.fetchall()

        conex.close()
        data = [dict(r) for r in rows]
        return {"message": "Lista de contactos", "data": data}
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error listando contactos: {e}")


@app.delete("/contactos/{contacto_id}")
def delete_contacto(contacto_id: int):
    try:
        conex = baseConnect()
        cursor = conex.cursor()
        cursor.execute("DELETE FROM contactos WHERE id = %s", (contacto_id,))
        conex.commit()
        affected = cursor.rowcount
        conex.close()
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
        conex = baseConnect()
        cursor = conex.cursor()
        cursor.execute("INSERT INTO mapas (placename, description, latitud, longitud, addresplace) VALUES (%s, %s, %s, %s, %s)",
            (map.placename, map.description, map.latitud, map.longitud, map.addresplace)
        )
        conex.commit()
        new_id = cursor.lastrowid
        conex.close()
        return {"message": "Lugar creado correctamente", "id": new_id, "data": map.dict()}
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error creando lugar: {e}")


@app.get("/mapas/")
def list_map():
    try:
        conex = baseConnect()
        cursor = conex.cursor()


        cursor.execute(

"SELECT id, placename, description, latitud, longitud, addresplace,score FROM mapas ORDER BY id DESC")
        rows = cursor.fetchall()

        conex.close()
        data = [dict(r) for r in rows]
        return {"message": "Lista de lugares", "data": data}
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error listando lugares: {e}")


@app.delete("/mapas/{map_id}")
def delete_map_entry(map_id: int):
    try:
        conex = baseConnect()

        cursor = conex.cursor()


        cursor.execute(

"DELETE FROM mapas WHERE id = %s", (map_id,))
        conex.commit()
        affected = cursor.rowcount
        conex.close()
        if affected == 0:
            raise HTTPException(status_code=404, detail="Lugar no encontrado")
        return {"message": "Lugar eliminado correctamente"}
    except HTTPException:
        raise
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error eliminando lugar: {e}")
    
    
    



    
@app.get("/coffee/")
def list_coffee():
    try:
        conex = baseConnect()
        cursor = conex.cursor()
        cursor.execute("SELECT id, coffee_type, coffe_image, description, video FROM coffee ORDER BY id DESC")
        rows = cursor.fetchall()
        conex.close()
        data = [dict(r) for r in rows]
        return {"message": "Lista de lugares", "data": data}
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error listando lugares: {e}")
    
@app.post("/coffee/", status_code=status.HTTP_201_CREATED)
def create_coffee(coffee: Coffee):
    try:
        conex = baseConnect()

        cursor = conex.cursor()


        cursor.execute(


            "INSERT INTO coffee (coffee_type, coffe_image, description, video) VALUES (%s, %s, %s, %s)",
            (coffee.coffee_type, coffee.coffee_image, coffee.description, coffee.video)
        )
        conex.commit()
        new_id = cur.lastrowid
        conex.close()
        return {"message": "Café creado correctamente", "id": new_id, "data": coffee.dict()}
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error creando café: {e}")
@app.delete("/coffee/{coffee_id}")
def delete_coffee(coffee_id: int):          
    try:
        conex = baseConnect()

        cursor = conex.cursor()


        cursor.execute(

"DELETE FROM coffee WHERE id = %s", (coffee_id,))
        conex.commit()
        affected = cursor.rowcount
        conex.close()
        if affected == 0:
            raise HTTPException(status_code=404, detail="Café no encontrado")
        return {"message": "Café eliminado correctamente"}
    except HTTPException:
        raise
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error eliminando café: {e}")
    


@app.post("/chat-simple/")
async def chat_simple(mensaje: str = Form(...)):
    try:
        respuesta = client.chat.completions.create(
            extra_headers={
                "HTTP-Referer": "",
                "X-Title": "",
            },
            model="gpt-oss-20b:free",
            messages=[
                {"role": "system", "content": "Eres un experto en café. Proporciona información sobre el café como su origen, sabor, características, además eres experto en identificar las comidas típicas de una ciudad."},
                {"role": "user", "content": f"¿{mensaje}?"}
            ]
        )
        respuesta_ia = respuesta.choices[0].message.content.strip()
        return JSONResponse(content={
            "mensaje": mensaje,
            "respuesta": respuesta_ia
        })
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)