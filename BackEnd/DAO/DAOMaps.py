from typing import Dict, Any
from BackEnd.DAO.DAOBase import BaseDAO
from BackEnd.BD_Mysql.ConectorDB import ConectorDB
import pymysql


class Maps(BaseDAO):
    
    def _execute_query(self, query: str, params: tuple = None, fetch: bool = True):
        """Método helper para ejecutar queries de forma segura"""
        conn = None
        cursor = None
        try:
            conn = ConectorDB().baseConnect()
            cursor = conn.cursor(pymysql.cursors.DictCursor)
            
            cursor.execute(query, params or ())
            
            if fetch:
                result = cursor.fetchall()
                return [dict(row) for row in result]
            else:
                conn.commit()
                return cursor.lastrowid
                
        except Exception as e:
            if conn:
                conn.rollback()
            raise RuntimeError(f"Database error: {e}")
        finally:
            if cursor:
                cursor.close()
            if conn and conn.open:
                conn.close()

    def enlistar_mapas(self) -> Dict[str, Any]:
        try:
            query = """
                SELECT 
                    m.id,
                    m.placename,
                    m.description,
                    m.latitud,
                    m.longitud,
                    m.addresplace,
                    m.score,
                    c.coffee_type,
                    c.description AS coffee_description,
                    c.coffe_image,
                    c.video
                FROM mapas AS m
                LEFT JOIN coffee AS c ON m.coffee_id = c.id
                ORDER BY m.id DESC
            """
            data = self._execute_query(query)
            return {"success": True, "data": data}
        except Exception as e:
            raise RuntimeError(f"MapsDAO enlistar_mapas failed: {e}")

    def get_by_id(self, map_id: int) -> Dict[str, Any]:
        try:
            query = """
                SELECT 
                    m.id,
                    m.placename,
                    m.description,
                    m.latitud,
                    m.longitud,
                    m.addresplace,
                    m.score,
                    m.coffee_id,
                    c.coffee_type,
                    c.description AS coffee_description,
                    c.coffe_image,
                    c.video
                FROM mapas AS m
                LEFT JOIN coffee AS c ON m.coffee_id = c.id
                WHERE m.id = %s 
                LIMIT 1
            """
            data = self._execute_query(query, (map_id,))
            if not data:
                return {"success": False, "error": "Map not found", "id": map_id}
            return {"success": True, "data": data[0]}
        except Exception as e:
            raise RuntimeError(f"MapsDAO get_by_id failed: {e}")

    def create(self, map_model) -> Dict[str, Any]:
        try:
            query = """
                INSERT INTO mapas 
                (placename, description, latitud, longitud, addresplace, score, coffee_id) 
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            values = (
                getattr(map_model, "placename", None),
                getattr(map_model, "description", None),
                getattr(map_model, "latitud", None),
                getattr(map_model, "longitud", None),
                getattr(map_model, "addresplace", None),
                getattr(map_model, "score", 0),
                getattr(map_model, "coffee_id", None),
            )
            
            new_id = self._execute_query(query, values, fetch=False)
            
            return {
                "success": True,
                "id": new_id,
                "data": map_model.dict() if hasattr(map_model, "dict") else dict(map_model),
            }
        except Exception as e:
            raise RuntimeError(f"MapsDAO create failed: {e}")

    def _execute_query(self, query: str, params: tuple = None, fetch: bool = True):
        """Método helper para ejecutar queries de forma segura"""
        conn = None
        cursor = None
        try:
            conn = ConectorDB().baseConnect()
            cursor = conn.cursor(pymysql.cursors.DictCursor)
            
            cursor.execute(query, params or ())
            
            if fetch:
                result = cursor.fetchall()
                return [dict(row) for row in result]
            else:
                conn.commit()
                # 🔹 IMPORTANTE: Para DELETE retornar rowcount
                return cursor.rowcount
                    
        except Exception as e:
            if conn:
                conn.rollback()
            raise RuntimeError(f"Database error: {e}")
        finally:
            if cursor:
                cursor.close()
            if conn and conn.open:
                conn.close()

    def update(self, map_id: int, fields: Dict[str, Any]) -> Dict[str, Any]:
        """Actualiza un mapa por ID con los campos especificados"""
        try:
            if not fields:
                return {"success": False, "error": "No fields to update"}
                
            # Campos permitidos para actualizar
            allowed_fields = {"placename", "description", "addresplace", "score", "coffee_id"}
            set_parts = []
            values = []
            
            # Construir la parte SET del query
            for field_name, field_value in fields.items():
                if field_name in allowed_fields:
                    set_parts.append(f"{field_name} = %s")
                    values.append(field_value)
                    
            if not set_parts:
                return {"success": False, "error": "No valid fields to update"}
                
            # Construir el query completo
            query = f"UPDATE mapas SET {', '.join(set_parts)} WHERE id = %s"
            values.append(map_id)
            
            print(f" Ejecutando UPDATE: {query}")
            print(f" Valores: {values}")
            
            # Ejecutar el query (fetch=False para UPDATE)
            affected_rows = self._execute_query(query, tuple(values), fetch=False)
            
            print(f" Filas afectadas: {affected_rows}")
            
            if affected_rows == 0:
                return {"success": False, "error": "Mapa not found", "id": map_id}
                
            return {"success": True, "updated_rows": affected_rows}
            
        except Exception as e:
            print(f" Error en update: {e}")
            raise RuntimeError(f"MapsDAO update failed: {e}")

    def delete(self, map_id: int) -> Dict[str, Any]:
        """Elimina un mapa por ID"""
        try:
            print(f"🔧 [DAO] Eliminando mapa ID: {map_id}")
            
            query = "DELETE FROM mapas WHERE id = %s"
            affected_rows = self._execute_query(query, (map_id,), fetch=False)
            
            print(f"🔧 [DAO] Filas afectadas: {affected_rows}")
            
            if affected_rows == 0:
                return {"success": False, "error": "Mapa not found", "id": map_id}
                
            return {"success": True, "deleted_rows": affected_rows}
            
        except Exception as e:
            print(f"❌ [DAO] Error en delete: {e}")
            raise RuntimeError(f"Maps delete failed: {e}")
        
    def get_by_coffee_id(self, coffee_id: int) -> Dict[str, Any]:
        try:
            query = """
                SELECT 
                    m.id,
                    m.placename,
                    m.description,
                    m.latitud,
                    m.longitud,
                    m.addresplace,
                    m.score
                FROM mapas AS m
                WHERE m.coffee_id = %s
                ORDER BY m.id DESC
            """
            data = self._execute_query(query, (coffee_id,))
            return {"success": True, "data": data}
        except Exception as e:
            raise RuntimeError(f"MapsDAO get_by_coffee_id failed: {e}")