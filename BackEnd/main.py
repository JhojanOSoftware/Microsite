import sqlite3
import traceback
from typing import List, Dict, Optional
from xmlrpc import client
from fastapi.responses import JSONResponse
from fastapi import FastAPI, HTTPException, status, Form, Request, Query
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter
from slowapi.util import get_remote_address
from openai  import OpenAI 
from BackEnd.models.Proyectos import Proyectos, Contactos, Map  
limiter = Limiter(key_func=get_remote_address)

client = OpenAI(
  base_url="https://openrouter.ai/api/v1",
  api_key="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",
)

# Inicializar la app de FastAPI
app = FastAPI(title="Actividad Microsite API")


# Aplicar el limiter a la app (opcional, para tenerlo disponible globalmente)
app.state.limiter = limiter

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
    
@app.post("/sgn")
async def obtener_significado(nombre: str = Form(...)):
    try:
        respuesta = client.chat.completions.create(
            extra_headers={
                "HTTP-Referer": "", # Optional. Site URL for rankings on openrouter.ai.
                "X-Title": "", # Optional. Site title for rankings on openrouter.ai.
            },
            model="gpt-oss-20b:free",
            messages=[
                {"role": "system", "content": "Eres un experto en etimología de nombres."},
                {"role": "user", "content": f"¿Cuál es el significado del nombre {nombre}?"}
            ]
        )

        significado = respuesta.choices[0].message.content.strip()
        return JSONResponse(content={
            "nombre": nombre,
            "significado": significado
        })
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)
    
@app.post("/feeling")
async def analizar_sentimiento(mensaje: str = Form(...)):
    try:
        respuesta = client.chat.completions.create(
            extra_headers={
                "HTTP-Referer": "",
                "X-Title": "",
            },
            model="gpt-oss-20b:free",
            messages=[
                {"role": "system", "content": "Eres un experto en análisis de sentimientos. Analiza el siguiente mensaje y responde únicamente con una de estas etiquetas: positivo, negativo o neutro."},
                {"role": "user", "content": f"Analiza el sentimiento del siguiente mensaje: '{mensaje}'"}
            ]
        )
        sentimiento = respuesta.choices[0].message.content.strip().lower()
        if sentimiento not in ["positivo", "negativo", "neutro"]:
            sentimiento = "neutro"
        return JSONResponse(content={
            "mensaje": mensaje,
            "sentimiento": sentimiento
        })
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)
    

@app.post("/curriculumanalisis")
async def analizar_pregunta(mensaje: str = Form(...)):
    # Prompt fijo con la información del CV
    system_prompt = """
    Eres un asistente especializado en analizar hojas de vida. Basa tus respuestas ÚNICAMENTE en la información proporcionada.

    INFORMACIÓN DEL CANDIDATO - JHOJAN ESTIBEN ORTIZ BAUTISTA:

    **EXPERIENCIA LABORAL:**
    1. TELEFÓNICA | MOVISTAR (Enero 2024 - Julio 2025)
       - Cargo: Desarrollador Python
       - Duración: 1.5 años (18 meses)
       - Proyecto principal: "Telefonica Automatización Permisos"
       - Logros: Mejoró eficiencia operativa en 25%, redujo errores en 40%
    
    2. KM2SOLUTIONS | MOVISTAR (Julio 2024 - Presente)
       - Cargo: Agente Bilingüe
       - Duración: Hasta la fecha actual
       - Funciones: Soporte al cliente en inglés para institución bancaria

    **EDUCACIÓN:**
    - Technologist in Data Network Management - SENA (Graduación: Julio 18, 2024)
    - Certificaciones: Scrum Fundamentals, RED HAT RH124, Cisco Cybersecurity, Python Essentials
    - Idiomas: Español (Nativo), Inglés (C1), Alemán (A1)

    **HABILIDADES TÉCNICAS:**
    - Lenguajes de programación: Python, SQL, JavaScript, Java
    - Bases de datos: MySQL, Oracle
    - Frameworks: Flask, React, Node.js
    - DevOps: Ubuntu Server, Bash, Wireshark, Nmap, Port Forwarding
    - Cybersecurity: Hashcat, Fail2Ban

    **PROYECTOS DESTACADOS:**
    - Automatización de servidores Linux y tareas DevOps
    - Permisos de automatización de Telefónica (Python, MySQL, Excel)

    **INSTRUCCIONES IMPORTANTES:**
    - Responde ÚNICAMENTE basado en la información proporcionada
    - Si la información no está disponible, indica "No tengo esa información en la hoja de vida"
    - Sé preciso con fechas y duraciones
    - Mantén las respuestas concisas y relevantes
    - No inventes información que no esté en el CV
    """
    try:
        respuesta = client.chat.completions.create(
            extra_headers={
                "HTTP-Referer": "",
                "X-Title": "",
            },
            model="gpt-oss-20b:free",
            messages=[
                {"role": "system", "content": f"{system_prompt}"},
                {"role": "user", "content": f"En base a la informacion proporcionada dando unicamente respuestas cortas y directas, '{mensaje}'"}
            ]
        )
        respuesta_texto = respuesta.choices[0].message.content.strip()
        return JSONResponse(content={
            "pregunta": mensaje,
            "respuesta": respuesta_texto
        })
    except Exception as e:
        error_message = f"Error procesando pregunta: {str(e)}"
        raise HTTPException(status_code=500, detail=error_message)