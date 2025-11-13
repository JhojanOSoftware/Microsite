import re
from typing import Dict, Any, List
from xmlrpc import client
from BackEnd.BD_Mysql.ConectorDB import ConectorDB
import pymysql
from fastapi.responses import JSONResponse, StreamingResponse
from fastapi import FastAPI, HTTPException, status, Form, Request, Query, Body, WebSocket, WebSocketDisconnect
import asyncio
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter
from slowapi.util import get_remote_address
from openai  import OpenAI 
from BackEnd.models.Proyectos import Proyectos, Contactos, Map ,Coffee
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
        "HTTP-Referer": "http://localhost:8000",
        "X-Title": "Actividad Microsite API",
        "Authorization": f"Bearer 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"
    }

)

# Inicializar la app de FastAPI
app = FastAPI(title="Actividad Microsite API")


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:5500",
        "http://localhost:5500",
        "http://localhost:3000",
        "http://127.0.0.1:8000",
        "null"  # permite origen file:// en navegadores
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DB_FILE = "Backend/proyects01_j0.db"


#DAO 
daocoffee = CoffeeDAO()
mapsdao = Maps()
proyectos_dao = ProyectosDAO()


# WebSocket connection manager for Coffee Assistant
class ConnectionManager:
    """Manage WebSocket and Server-Sent Events (SSE) subscribers.

    - active_connections: list of WebSocket objects
    - sse_queues: list of asyncio.Queue objects used to push SSE events to connected clients
    """
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.sse_queues: List[asyncio.Queue] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    def register_sse(self, queue: asyncio.Queue):
        self.sse_queues.append(queue)

    def unregister_sse(self, queue: asyncio.Queue):
        try:
            self.sse_queues.remove(queue)
        except ValueError:
            pass

    async def broadcast_message(self, payload: dict):
        """Broadcast a payload (dict) to all WebSocket and SSE clients."""
        text = json.dumps(payload, ensure_ascii=False)

        to_remove = []
        for ws in list(self.active_connections):
            try:
                await ws.send_text(text)
            except Exception:
                to_remove.append(ws)
        for ws in to_remove:
            self.disconnect(ws)

        for q in list(self.sse_queues):
            try:
                q.put_nowait(payload)
            except Exception:
                pass


manager = ConnectionManager()



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

def root():
    inpath = os.path.join("/index.html")
    with open(inpath, 'r', encoding='utf-8') as file:
        content = file.read()
    return JSONResponse(content=content)


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
    


@app.get("/")
def root():
    inpath = os.path.join("/index.html")
    with open(inpath, 'r', encoding='utf-8') as file:
        content = file.read()
    return JSONResponse(content=content)


@app.get("/CoffeeAssistance.html")
def root():
    inpath = os.path.join("/CoffeeAssistance.html")
    with open(inpath, 'r', encoding='utf-8') as file:
        content = file.read()
    return JSONResponse(content=content)




@app.post("/proyectos/", status_code=status.HTTP_201_CREATED)
def crear_proyecto(proyecto: Proyectos):
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
def eliminar_proyecto(proyecto_id: int):
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
def actualizar_proyecto(proyecto_id: int, proyecto_update: Dict[str, Any]):
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
                {"role": "system", "content": "Eres un experto en café y en comidas típicas como te dan una ciudad tu hablas que cafe se toma mas alla. Proporciona información sobre el café como su origen, sabor, características, además eres experto en identificar las comidas típicas de una ciudad y las das de manera breve sin extenderte mencionando 3 comidas favoritas de dicha ciudad."},
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

@app.get("/iniciarasistente")
def chat_welcome():
    return {
        "message": "¡Hola! Soy tu asistente de café ☕\nPuedes preguntarme cosas como:\n• 'Sitios con puntuación mayor a 4'\n• 'Cafés arabica con buen rating'\n• 'Los mejores cafés cerca de mí'\n• 'Sitios con rating sobre 4.5'",
        "examples": [
            "Sitios con puntuación mayor a 4",
            "Cafés arabica con alta calificación", 
            "Los mejores cafés robusta",
            "Sitios con rating excelente"
        ],
        "timestamp": datetime.now().isoformat()
    }

@app.get("/assistant/mapas-score")
def get_coffee_shops(
    min_rating: float = Query(None, description="Puntuación mínima"),
):
    try:
        conex = baseConnect()
        cursor = conex.cursor()

        query = "SELECT * FROM mapas WHERE 4 < score"
        params = []
        
        if min_rating is not None:
            query += " AND score >= %s"
            params.append(min_rating)
            
       
        
        query += " ORDER BY score DESC"
        
        cursor.execute(query, params)
        resultados = cursor.fetchall()
        conex.close()
        
        return {
            "count": len(resultados),
            "results": resultados,
            "filters_applied": {
                "min_rating": min_rating,
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error obteniendo sitios: {e}")
    
@app.get("/assistant/mapas-type")
def get_coffee_shops(
    coffee_type: str = Query(None, description="Tipo de café: arabica, robusta, liberica, excelsa"),
):
    try:
        conex = baseConnect()
        cursor = conex.cursor()

        query = "SELECT coffee_type , description FROM coffee WHERE 1=1"
        params = []

        if coffee_type is not None:
            query += " AND coffee_type = %s"
            params.append(coffee_type.lower())

        
        cursor.execute(query, params)
        resultados = cursor.fetchall()
        conex.close()
        
        return {
            "count": len(resultados),
            "results": resultados,
            "filters_applied": {
                "Coffee_type": coffee_type,
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error obteniendo sitios: {e}")
    
@app.post("/api/chat/message")
def process_chat_message(message_data: dict = Body(...)):
    try:
        mensaje = message_data.get("message", "").lower()
        usuario = message_data.get("user", "Usuario")
        
        print(f" Mensaje recibido de {usuario}: {mensaje}")
        
        # Procesar consulta natural
        criterios = {}
        
        # Detectar puntuación mínima
        if 'puntuación mayor a' in mensaje or 'rating mayor a' in mensaje or 'puntuacion mayor a' in mensaje:
            numeros = re.findall(r'(\d+\.?\d*)', mensaje)
            if numeros:
                criterios['min_rating'] = float(numeros[0])
        elif 'buena puntuación' in mensaje or 'alto rating' in mensaje or 'buena puntuacion' in mensaje:
            criterios['min_rating'] = 4.0
        elif 'excelente puntuación' in mensaje or 'rating excelente' in mensaje or 'excelente puntuacion' in mensaje:
            criterios['min_rating'] = 4.5
        
        # Detectar tipo de café
        tipos_cafe = [ 'Espresso ' ,    'Americano ' ,      'Cappuccino ' ,     'Latte ' ,          'Macchiato ' ,      'Mocha ' ,          'Flat White ' ,     'Café con Leche ' ,
'Ristretto ' ,       'Café Cortado ' ,   'Café Irish ' ,     'Affogato ' ,       'Café Vienés ' ,    'Cold Brew ' ,      'Café Turco ']
        tipo_cafe_encontrado = None
        for tipo in tipos_cafe:
            if tipo in mensaje:
                tipo_cafe_encontrado = tipo
                break
        
        # Buscar en ambas tablas
        conex = baseConnect()
        cursor = conex.cursor()
        
        # PRIMERO: Buscar en tabla MAPAS (sitios de café)
        query_mapas = "SELECT * FROM mapas WHERE 1=1"
        params_mapas = []
        
        if 'min_rating' in criterios:
            query_mapas += " AND score >= %s"
            params_mapas.append(criterios['min_rating'])
        
        query_mapas += " ORDER BY score DESC"
        
        cursor.execute(query_mapas, params_mapas)
        resultados_mapas = cursor.fetchall()
        
        # SEGUNDO: Buscar tipos de café si se especificó
        resultados_coffee = []
        if tipo_cafe_encontrado:
            query_coffee = "SELECT * FROM coffee WHERE LOWER(coffee_type) = %s"
            cursor.execute(query_coffee, [tipo_cafe_encontrado])
            resultados_coffee = cursor.fetchall()
        
        conex.close()
        
        # Generar respuesta amigable combinando resultados
        if not resultados_mapas and not resultados_coffee:
            respuesta_chat = " No encontré sitios que coincidan con tu búsqueda. "
            if tipo_cafe_encontrado:
                respuesta_chat += f"El tipo de café {tipo_cafe_encontrado} no está disponible en nuestros sitios registrados."
            else:
                respuesta_chat += "¿Podrías intentar con otros criterios?"
                
        else:
            respuesta_chat = ""
            
            # Mostrar sitios de café encontrados
            if resultados_mapas:
                respuesta_chat += f" Encontré {len(resultados_mapas)} sitio(s) de café para tu consulta:\n\n"
                
                for i, sitio in enumerate(resultados_mapas, 1):
                    respuesta_chat += f"{i}. {sitio['placename']} ⭐ {sitio['score']}/5  "
                    respuesta_chat += f"   Dirección: {sitio['addresplace']}\n"
                    
            
            # Mostrar información de tipos de café
            if resultados_coffee:
                respuesta_chat += f"ℹ️  Información sobre café {tipo_cafe_encontrado.title()}:\n\n"
                for i, coffee_info in enumerate(resultados_coffee, 1):
                    respuesta_chat += f"{i}. {coffee_info['coffee_type'].title()}\n"
                    respuesta_chat += f"   Descripción: {coffee_info['description']}\n"
                    respuesta_chat += "\n"
            
            respuesta_chat += "¿Te gustaría saber más sobre algún sitio en particular?"
        
        return {
            "response": respuesta_chat,
            "results": {
                "sitios_cafe": resultados_mapas,
                "tipos_cafe": resultados_coffee
            },
            "criteria_used": criterios,
            "timestamp": datetime.now().isoformat(),
            "user": usuario
        }
        
    except Exception as e:
        print(f"❌ Error en process_chat_message: {e}")
        traceback.print_exc()
        raise HTTPException(
            status_code=500, 
            detail=f"Error procesando mensaje: {e}"
        )


# WebSocket endpoint for Coffee Assistance
@app.websocket("/ws/coffee-assistant")
async def websocket_coffee_assistant(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        # welcome message (same spirit as /iniciarasistente)
        welcome_msg = {
            "type": "welcome",
            "message": "¡Hola! Soy tu asistente de café ☕\nPuedes preguntarme cosas como:\n• 'Sitios con puntuación mayor a 4'\n• 'Cafés con buen rating'\n• 'Los mejores cafés cerca de mí'",
            "timestamp": datetime.now().isoformat(),
        }
        await websocket.send_text(json.dumps(welcome_msg))

        while True:
            raw = await websocket.receive_text()
            try:
                message_data = json.loads(raw)
            except Exception:
                await websocket.send_text(json.dumps({
                    "type": "error",
                    "message": "Formato inválido. Envía JSON con { message, user }",
                    "timestamp": datetime.now().isoformat(),
                }))
                continue

            # Reuse existing processing logic inline (same as process_chat_message)
            mensaje = (message_data.get("message", "") or "").lower()
            usuario = message_data.get("user", "Usuario")

            criterios = {}
            if 'puntuación mayor a' in mensaje or 'rating mayor a' in mensaje or 'puntuacion mayor a' in mensaje:
                numeros = re.findall(r'(\d+\.?\d*)', mensaje)
                if numeros:
                    criterios['min_rating'] = float(numeros[0])
            elif 'buena puntuación' in mensaje or 'alto rating' in mensaje or 'buena puntuacion' in mensaje:
                criterios['min_rating'] = 4.0
            elif 'excelente puntuación' in mensaje or 'rating excelente' in mensaje or 'excelente puntuacion' in mensaje:
                criterios['min_rating'] = 4.5

            tipos_cafe = [ 'Espresso ' ,    'Americano ' ,      'Cappuccino ' ,     'Latte ' ,          'Macchiato ' ,      'Mocha ' ,          'Flat White ' ,     'Café con Leche ' ,
'Ristretto ' ,       'Café Cortado ' ,   'Café Irish ' ,     'Affogato ' ,       'Café Vienés ' ,    'Cold Brew ' ,      'Café Turco ']
            tipo_cafe_encontrado = None
            for tipo in tipos_cafe:
                if tipo in mensaje:
                    tipo_cafe_encontrado = tipo
                    break

            conex = baseConnect()
            cursor = conex.cursor()

            query_mapas = "SELECT * FROM mapas WHERE 1=1"
            params_mapas = []
            if 'min_rating' in criterios:
                query_mapas += " AND score >= %s"
                params_mapas.append(criterios['min_rating'])
            query_mapas += " ORDER BY score DESC"
            cursor.execute(query_mapas, params_mapas)
            resultados_mapas = cursor.fetchall()

            resultados_coffee = []
            if tipo_cafe_encontrado:
                query_coffee = "SELECT * FROM coffee WHERE LOWER(coffee_type) = %s"
                cursor.execute(query_coffee, [tipo_cafe_encontrado])
                resultados_coffee = cursor.fetchall()

            conex.close()

            if not resultados_mapas and not resultados_coffee:
                respuesta_chat = " No encontré sitios que coincidan con tu búsqueda. "
                if tipo_cafe_encontrado:
                    respuesta_chat += f"El tipo de café {tipo_cafe_encontrado} no está disponible en nuestros sitios registrados."
                else:
                    respuesta_chat += "¿Podrías intentar con otros criterios?"
            else:
                respuesta_chat = ""
                if resultados_mapas:
                    respuesta_chat += f" Encontré {len(resultados_mapas)} sitio(s) de café para tu consulta:\n\n"
                    for i, sitio in enumerate(resultados_mapas, 1):
                        respuesta_chat += f"{i}. {sitio['placename']} ⭐ {sitio['score']}/5  "
                        respuesta_chat += f"   Dirección: {sitio['addresplace']}\n"
                if resultados_coffee:
                    respuesta_chat += f"ℹ️  Información sobre café {tipo_cafe_encontrado.title()}:\n\n"
                    for i, coffee_info in enumerate(resultados_coffee, 1):
                        respuesta_chat += f"{i}. {coffee_info['coffee_type'].title()}\n"
                        respuesta_chat += f"   Descripción: {coffee_info['description']}\n\n"
                respuesta_chat += "¿Te gustaría saber más sobre algún sitio en particular?"

            response_ws = {
                "type": "chat_response",
                "response": respuesta_chat,
                "results": {
                    "sitios_cafe": resultados_mapas,
                    "tipos_cafe": resultados_coffee,
                },
                "criteria_used": criterios,
                "timestamp": datetime.now().isoformat(),
                "user": usuario,
            }
            await websocket.send_text(json.dumps(response_ws))

    except WebSocketDisconnect:
        manager.disconnect(websocket)
        print("🔴 [WebSocket] Cliente desconectado")
    except Exception as e:
        err = {
            "type": "error",
            "message": f"Error procesando mensaje: {str(e)}",
            "timestamp": datetime.now().isoformat(),
        }
        try:
            await websocket.send_text(json.dumps(err))
        except Exception:
            pass
        manager.disconnect(websocket)


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "active_connections": len(manager.active_connections),
    }


# SSE fallback endpoint: streams a single chat response event for simple clients
@app.get("/sse/coffee")
def sse_coffee(message: str = Query(..., description="Mensaje del usuario"), user: str = Query("Usuario", description="Nombre del usuario")):
    def generate_event(payload: dict) -> str:
        # Server-Sent Events format: optional event name, then data, then double newline
        return f"data: {json.dumps(payload, ensure_ascii=False)}\n\n"

    try:
        # Reutilizar la misma lógica de procesamiento que en WebSocket/REST
        mensaje = (message or "").lower()

        criterios = {}
        if 'puntuación mayor a' in mensaje or 'rating mayor a' in mensaje or 'puntuacion mayor a' in mensaje:
            numeros = re.findall(r'(\d+\.?\d*)', mensaje)
            if numeros:
                criterios['min_rating'] = float(numeros[0])
        elif 'buena puntuación' in mensaje or 'alto rating' in mensaje or 'buena puntuacion' in mensaje:
            criterios['min_rating'] = 4.0
        elif 'excelente puntuación' in mensaje or 'rating excelente' in mensaje or 'excelente puntuacion' in mensaje:
            criterios['min_rating'] = 4.5

        tipos_cafe = [ 'Espresso ' ,    'Americano ' ,      'Cappuccino ' ,     'Latte ' ,          'Macchiato ' ,      'Mocha ' ,          'Flat White ' ,     'Café con Leche ' ,
'Ristretto ' ,       'Café Cortado ' ,   'Café Irish ' ,     'Affogato ' ,       'Café Vienés ' ,    'Cold Brew ' ,      'Café Turco ']
        tipo_cafe_encontrado = None
        for tipo in tipos_cafe:
            if tipo in mensaje:
                tipo_cafe_encontrado = tipo
                break

        conex = baseConnect()
        cursor = conex.cursor()

        query_mapas = "SELECT * FROM mapas WHERE 1=1"
        params_mapas = []
        if 'min_rating' in criterios:
            query_mapas += " AND score >= %s"
            params_mapas.append(criterios['min_rating'])
        query_mapas += " ORDER BY score DESC"
        cursor.execute(query_mapas, params_mapas)
        resultados_mapas = cursor.fetchall()

        resultados_coffee = []
        if tipo_cafe_encontrado:
            query_coffee = "SELECT * FROM coffee WHERE LOWER(coffee_type) = %s"
            cursor.execute(query_coffee, [tipo_cafe_encontrado])
            resultados_coffee = cursor.fetchall()

        conex.close()

        if not resultados_mapas and not resultados_coffee:
            respuesta_chat = " No encontré sitios que coincidan con tu búsqueda. "
            if tipo_cafe_encontrado:
                respuesta_chat += f"El tipo de café {tipo_cafe_encontrado} no está disponible en nuestros sitios registrados."
            else:
                respuesta_chat += "¿Podrías intentar con otros criterios?"
        else:
            respuesta_chat = ""
            if resultados_mapas:
                respuesta_chat += f" Encontré {len(resultados_mapas)} sitio(s) de café para tu consulta:\n\n"
                for i, sitio in enumerate(resultados_mapas, 1):
                    respuesta_chat += f"{i}. {sitio['placename']} ⭐ {sitio['score']}/5  "
                    respuesta_chat += f"   Dirección: {sitio['addresplace']}\n"
            if resultados_coffee:
                respuesta_chat += f"ℹ️  Información sobre café {tipo_cafe_encontrado.title()}:\n\n"
                for i, coffee_info in enumerate(resultados_coffee, 1):
                    respuesta_chat += f"{i}. {coffee_info['coffee_type'].title()}\n"
                    respuesta_chat += f"   Descripción: {coffee_info['description']}\n\n"
            respuesta_chat += "¿Te gustaría saber más sobre algún sitio en particular?"

        payload = {
            "type": "chat_response",
            "response": respuesta_chat,
            "results": {
                "sitios_cafe": resultados_mapas,
                "tipos_cafe": resultados_coffee,
            },
            "criteria_used": criterios,
            "timestamp": datetime.now().isoformat(),
            "user": user,
        }

        return StreamingResponse(iter([generate_event(payload)]), media_type="text/event-stream")

    except Exception as e:
        error_payload = {
            "type": "error",
            "message": f"Error procesando mensaje: {str(e)}",
            "timestamp": datetime.now().isoformat(),
        }
        return StreamingResponse(iter([generate_event(error_payload)]), media_type="text/event-stream")


@app.get("/sse/coffee-chat")
async def sse_coffee_chat(request: Request):
        """Persistent SSE endpoint: clients stay connected and receive TCP/WebSocket broadcast messages."""
        queue: asyncio.Queue = asyncio.Queue()
        manager.register_sse(queue)

        async def event_generator():
            try:
                while True:
                    # If client disconnected, stop
                    if await request.is_disconnected():
                        break
                    try:
                        payload = await queue.get()
                    except asyncio.CancelledError:
                        break
                    data = json.dumps(payload, ensure_ascii=False)
                    yield f"data: {data}\n\n"
            finally:
                manager.unregister_sse(queue)

        return StreamingResponse(event_generator(), media_type="text/event-stream")


@app.get("/sse/coffee-query")
def sse_coffee_query(message: str = Query(...), user: str = Query("Usuario")):
        """SSE endpoint that responds once for a specific query (convenient for SSE-capable clients)."""
        def generate_event(payload: dict) -> str:
            return f"data: {json.dumps(payload, ensure_ascii=False)}\n\n"

        # Reuse the same logic as sse_coffee but under a different route name
        return sse_coffee(message=message, user=user)


@app.get("/status")
def status():
        return {
            "http": "up",
            "websocket": {"active_connections": len(manager.active_connections)},
            "sse": {"subscribers": len(manager.sse_queues)},
            "timestamp": datetime.now().isoformat()
        }


# TCP testing endpoints removed per request — only SSE/WebSocket remain