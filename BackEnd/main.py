import re
from typing import Dict, Any, List
from xmlrpc import client
from BackEnd.BD_Mysql.ConectorDB import ConectorDB
import pymysql
from fastapi.responses import JSONResponse, StreamingResponse, HTMLResponse, RedirectResponse
from pathlib import Path
from fastapi import FastAPI, HTTPException, status, Form, Request, Query, Body
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter
from slowapi.util import get_remote_address
from openai  import OpenAI 
from BackEnd.models.Proyectos import Proyectos, Contactos, Map ,Coffee
import hashlib
limiter = Limiter(key_func=get_remote_address)
from fastapi.staticfiles import StaticFiles
import os
import traceback 
from datetime import datetime
import json
from BackEnd.DAO.DAOCoffee import CoffeeDAO
from BackEnd.DAO.DAOMaps import Maps
from BackEnd.DAO.DAOContactos import ContactosDAO
from BackEnd.DAO.DAOProyectos import ProyectosDAO




client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key="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",
    default_headers={
        "HTTP-Referer": "http://localhost:5000",
        "X-Title": "Actividad Microsite API",
        "Authorization": f"Bearer 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"
    }

)

# Inicializar la app de FastAPI
app = FastAPI(title="Actividad Microsite API")


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:8000",
        "http://localhost:8000",
        "http://localhost:3000",
        "http://127.0.0.1:5000",
        "http://127.0.0.1:5500",
        "http://localhost:5500",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


#DAO 
daocoffee = CoffeeDAO()
mapsdao = Maps()
proyectos_dao = ProyectosDAO()



def baseConnect():
    return pymysql.connect(
        host='localhost',
        user='jhojan',
        password='Myestrell@1929*',
        database='proyectoj0',
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor
    )
# Aplicar el limiter a la app (opcional, para tenerlo disponible globalmente)
app.state.limiter = limiter

# Base project directory (two levels up from this file: project root)
BASE_DIR = Path(__file__).resolve().parent.parent

# 🔹 Ruta absoluta a tu carpeta de imágenes
images_path = os.path.join(os.getcwd(), "Frontend", "Images")

# 🔹 Montar la carpeta como estático
app.mount("/images", StaticFiles(directory=images_path), name="images")
# 🔹 Montar la carpeta Frontend para servir CSS/JS/plantillas estáticas cuando el backend sirve HTML
frontend_dir = BASE_DIR / "Frontend"
if frontend_dir.exists():
    app.mount("/Frontend", StaticFiles(directory=str(frontend_dir)), name="frontend")
else:
    print(f"⚠️ Frontend directory not found at {frontend_dir}")

# 🔹 Montar la carpeta BackEnd para servir GetAPI.js
backend_dir = BASE_DIR / "BackEnd"
if backend_dir.exists():
    app.mount("/BackEnd", StaticFiles(directory=str(backend_dir)), name="backend")
else:
    print(f"⚠️ BackEnd directory not found at {backend_dir}")
# Ajusta orígenes según donde sirvas el frontend



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





@app.on_event("startup")
def startup():
    ensure_db()
    print("🔸 Startup tasks completed: DB ensured")
    


@app.get("/", response_class=HTMLResponse)
def root():
    """Serve the main index.html page."""
    inpath = BASE_DIR / "index.html"
    if not inpath.exists():
        return HTMLResponse(content="<h1>Página no encontrada</h1>", status_code=404)
    try:
        content = inpath.read_text(encoding='utf-8')
        return HTMLResponse(content=content, status_code=200)
    except Exception as e:
        return HTMLResponse(content=f"<h1>Error al leer index.html: {e}</h1>", status_code=500)


@app.get("/index.html", response_class=HTMLResponse)
def serve_index():
    """Serve the main index.html file from project root."""
    inpath = BASE_DIR / "index.html"
    if not inpath.exists():
        return HTMLResponse(content="<h1>index.html no encontrado</h1>", status_code=404)
    try:
        content = inpath.read_text(encoding='utf-8')
        return HTMLResponse(content=content, status_code=200)
    except Exception as e:
        return HTMLResponse(content=f"<h1>Error al leer index.html: {e}</h1>", status_code=500)








@app.post("/proyectos/", status_code=status.HTTP_201_CREATED)
def crear_proyecto(request: Request, proyecto: Proyectos):
    try:
        result = proyectos_dao.create(proyecto)
        if result["success"]:
            return {
                "message": "Proyecto creado correctamente", 
                "id": result["id"], 
                "data": result["data"]
            }
        else:
            raise HTTPException(status_code=400, detail=result["error"])
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creando proyecto: {e}")

@app.get("/proyectos/")
def listar_proyectos():
    try:
        dao = ProyectosDAO()
        result = dao.enlistar_proyectos()
        return {"data": result["data"]}  # Data retornada en formato JSon
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listando proyectos: {e}")

@app.delete("/proyectos/{proyecto_id}")
def eliminar_proyecto(request: Request, proyecto_id: int):
    try:
        result = proyectos_dao.delete(proyecto_id)
        if result["success"]:
            return {"message": "Proyecto eliminado correctamente"}
        else:
            raise HTTPException(status_code=404, detail="Proyecto no encontrado")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error eliminando proyecto: {e}")

# Endpoints adicionales que puedes agregar
@app.get("/proyectos/{proyecto_id}")
def obtener_proyecto(proyecto_id: int):
    try:
        result = proyectos_dao.get_by_id(proyecto_id)
        if result["success"]:
            return {"message": "Proyecto encontrado", "data": result["data"]}
        else:
            raise HTTPException(status_code=404, detail="Proyecto no encontrado")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error obteniendo proyecto: {e}")

@app.put("/proyectos/{proyecto_id}")
def actualizar_proyecto(request: Request, proyecto_id: int, proyecto_update: Dict[str, Any]):
    try:
        result = proyectos_dao.update(proyecto_id, proyecto_update)
        if result["success"]:
            return {"message": "Proyecto actualizado correctamente", "updated_rows": result["updated_rows"]}
        else:
            raise HTTPException(status_code=404, detail=result["error"])
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error actualizando proyecto: {e}")


@app.post("/contactos/", status_code=status.HTTP_201_CREATED)
def crear_contacto(contacto: Contactos):
    try:
        dao = ContactosDAO()
        result = dao.create(contacto)
        if result["success"]:
            return {
                "message": "Contacto creado correctamente", 
                "id": result["id"], 
                "data": result["data"]
            }
        else:
            raise HTTPException(status_code=400, detail=result["error"])
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creando contacto: {e}")

@app.get("/contactos/")
def listar_contactos():
    try:
        dao = ContactosDAO()
        result = dao.enlistar_contactos()
        return {"data": result["data"]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listando contactos: {e}")

@app.get("/contactos/{contacto_id}")
def obtener_contacto(contacto_id: int):
    try:
        dao = ContactosDAO()
        result = dao.get_by_id(contacto_id)
        if result["success"]:
            return {"data": result["data"]}
        else:
            raise HTTPException(status_code=404, detail="Contacto no encontrado")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error obteniendo contacto: {e}")

@app.delete("/contactos/{contacto_id}")
def delete_contacto(contacto_id: int):
    try:
        dao = ContactosDAO()
        result = dao.delete(contacto_id)
        if result["success"]:
            return {"message": "Contacto eliminado correctamente"}
        else:
            raise HTTPException(status_code=404, detail="Contacto no encontrado")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error eliminando contacto: {e}")



@app.post("/mapas/", status_code=status.HTTP_201_CREATED)
def createnode(request: Request, map: Map):
    try:
        result = mapsdao.create(map)
        if result["success"]:
            return {"message": "Lugar creado correctamente", "id": result["id"], "data": result["data"]}
        else:
            raise HTTPException(status_code=400, detail=result["error"])
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creando lugar: {e}")

@app.get("/mapas/")
def list_map():
    try:
        return mapsdao.enlistar_mapas()
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error listando lugares: {e}")
    
@app.delete("/mapas/{mapa_id}")
def eliminar_mapa(request: Request, mapa_id: int):
    try:
        print(f" [SERVER] DELETE recibido para mapa ID: {mapa_id}")
        
        # 🔹 CORRECCIÓN: Crear instancia de Maps y llamar al método delete
        dao = Maps()  # Instanciar la clase
        result = dao.delete(mapa_id)  # Llamar al método
        
        print(f" [SERVER] Resultado del delete: {result}")
        
        if result["success"]:
            return {
                "message": "Mapa eliminado correctamente", 
                "deleted_rows": result["deleted_rows"]
            }
        else:
            raise HTTPException(status_code=404, detail=result["error"])
            
    except Exception as e:
        print(f" [SERVER] Error en eliminar_mapa: {e}")
        raise HTTPException(status_code=500, detail=f"Error eliminando mapa: {e}")

@app.get("/mapas/{mapa_id}")
def obtener_mapa(mapa_id: int):
        try:
            dao = mapsdao.get_by_id(mapa_id)
            if dao["success"]:
                return {"data": dao["data"]}
            else:
                raise HTTPException(status_code=404, detail="Mapa no encontrado")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error obteniendo mapa: {e}")


@app.put("/mapas/{mapa_id}")
def actualizar_mapa(request: Request, mapa_id: int, mapa_update: Dict[str, Any]):
    try:
        print(f" [SERVER] PUT recibido para mapa {mapa_id}")
        print(f" [SERVER] Datos recibidos: {mapa_update}")
        
        dao = Maps()
        result = dao.update(mapa_id, mapa_update)
        
        if result["success"]:
            return {
                "message": "Mapa actualizado correctamente", 
                "updated_rows": result["updated_rows"]
            }
        else:
            raise HTTPException(status_code=404, detail=result["error"])
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error actualizando mapa: {e}")    
@app.get("/coffee/")
def list_coffee():
    try:
        return daocoffee.enlistarcoffees()
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error listando cafés: {e}")

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
        new_id = cursor.lastrowid
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
    



@app.post("/mapas/", status_code=status.HTTP_201_CREATED)
def createnode(map: Map):
    try:
        result = mapsdao.create(map)
        if result["success"]:
            return {"message": "Lugar creado correctamente", "id": result["id"], "data": result["data"]}
        else:
            raise HTTPException(status_code=400, detail=result["error"])
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creando lugar: {e}")

@app.get("/mapas/")
def list_map():
    try:
        return mapsdao.enlistar_mapas()
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error listando lugares: {e}")
    
@app.delete("/mapas/{mapa_id}")
def eliminar_mapa(mapa_id: int):
    try:
        print(f" [SERVER] DELETE recibido para mapa ID: {mapa_id}")
        
        # 🔹 CORRECCIÓN: Crear instancia de Maps y llamar al método delete
        dao = Maps()  # Instanciar la clase
        result = dao.delete(mapa_id)  # Llamar al método
        
        print(f" [SERVER] Resultado del delete: {result}")
        
        if result["success"]:
            return {
                "message": "Mapa eliminado correctamente", 
                "deleted_rows": result["deleted_rows"]
            }
        else:
            raise HTTPException(status_code=404, detail=result["error"])
            
    except Exception as e:
        print(f" [SERVER] Error en eliminar_mapa: {e}")
        raise HTTPException(status_code=500, detail=f"Error eliminando mapa: {e}")

@app.get("/mapas/{mapa_id}")
def obtener_mapa(mapa_id: int):
        try:
            dao = mapsdao.get_by_id(mapa_id)
            if dao["success"]:
                return {"data": dao["data"]}
            else:
                raise HTTPException(status_code=404, detail="Mapa no encontrado")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error obteniendo mapa: {e}")


@app.put("/mapas/{mapa_id}")
def actualizar_mapa(mapa_id: int, mapa_update: Dict[str, Any]):
    try:
        print(f" [SERVER] PUT recibido para mapa {mapa_id}")
        print(f" [SERVER] Datos recibidos: {mapa_update}")
        
        dao = Maps()
        result = dao.update(mapa_id, mapa_update)
        
        if result["success"]:
            return {
                "message": "Mapa actualizado correctamente", 
                "updated_rows": result["updated_rows"]
            }
        else:
            raise HTTPException(status_code=404, detail=result["error"])
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error actualizando mapa: {e}")    