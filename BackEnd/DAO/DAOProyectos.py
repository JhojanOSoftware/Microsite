from typing import Optional, Dict, Any
from BackEnd.DAO.DAOBase import BaseDAO
from BackEnd.BD_Mysql.ConectorDB import ConectorDB
import pymysql


class ProyectosDAO(BaseDAO):
    
    def __init__(self, conn: Optional[pymysql.connections.Connection] = None):
        if conn:
            self.conn = conn
            self._owns_connection = False
        else:
            self.conn = ConectorDB().baseConnect()
            self._owns_connection = True

    def close(self) -> None:
        try:
            if self.conn and self._owns_connection:
                self.conn.close()
        finally:
            self.conn = None

    def enlistar_proyectos(self) -> Dict[str, Any]:
        
        try:
            cursor = self.conn.cursor(pymysql.cursors.DictCursor)
            cursor.execute(
                "SELECT id, nombre, description, imagen, fecha, linkgithub, linkvideo "
                "FROM proyectos ORDER BY id DESC"
            )
            rows = cursor.fetchall()
            return {"success": True, "data": [dict(r) for r in rows]}
        except Exception as e:
            raise RuntimeError(f"ProyectosDAO enlistar_proyectos failed: {e}")
        finally:
            if cursor:
                cursor.close()
            if self._owns_connection:
                self.close()

    def get_by_id(self, proyecto_id: int) -> Dict[str, Any]:
        """
        Devuelve un proyecto por su ID.
        SQL: SELECT ... FROM proyectos WHERE id = %s LIMIT 1;
        """
        cursor = None
        try:
            cursor = self.conn.cursor(pymysql.cursors.DictCursor)
            cursor.execute(
                "SELECT id, nombre, description, imagen, fecha, linkgithub, linkvideo "
                "FROM proyectos WHERE id = %s LIMIT 1",
                (proyecto_id,),
            )
            row = cursor.fetchone()
            if not row:
                return {"success": False, "error": "Proyecto not found", "id": proyecto_id}
            return {"success": True, "data": dict(row)}
        except Exception as e:
            raise RuntimeError(f"ProyectosDAO get_by_id failed: {e}")
        finally:
            if cursor:
                cursor.close()
            if self._owns_connection:
                self.close()

    def create(self, proyecto_model) -> Dict[str, Any]:
        """
        Inserta un nuevo proyecto en la tabla.
        Parámetro: objeto Pydantic del proyecto (proyecto_model)
        SQL: INSERT INTO proyectos (nombre, description, imagen, fecha, linkgithub, linkvideo) 
             VALUES (%s, %s, %s, %s, %s, %s)
        """
        cursor = None
        try:
            cursor = self.conn.cursor()
            sql = """
                INSERT INTO proyectos 
                (nombre, description, imagen, fecha, linkgithub, linkvideo) 
                VALUES (%s, %s, %s, %s, %s, %s)
            """
            values = (
                getattr(proyecto_model, "nombre", None),
                getattr(proyecto_model, "description", None),
                getattr(proyecto_model, "imagen", None),
                getattr(proyecto_model, "fecha", None),
                getattr(proyecto_model, "linkgithub", None),
                getattr(proyecto_model, "linkvideo", None),
            )
            cursor.execute(sql, values)
            self.conn.commit()
            new_id = cursor.lastrowid
            return {
                "success": True,
                "id": new_id,
                "data": proyecto_model.dict() if hasattr(proyecto_model, "dict") else dict(proyecto_model),
            }
        except Exception as e:
            self.conn.rollback()
            raise RuntimeError(f"ProyectosDAO create failed: {e}")
        finally:
            if cursor:
                cursor.close()
            if self._owns_connection:
                self.close()

    def update(self, proyecto_id: int, fields: Dict[str, Any]) -> Dict[str, Any]:
        """
        Actualiza los campos de un proyecto existente por ID.
        fields: diccionario con columnas a actualizar.
        SQL: UPDATE proyectos SET col1=%s, col2=%s WHERE id=%s;
        """
        cursor = None
        try:
            if not fields:
                return {"success": False, "error": "No fields to update"}
            allowed = {"nombre", "description", "imagen", "fecha", "linkgithub", "linkvideo"}
            set_parts = []
            values = []
            for k, v in fields.items():
                if k in allowed:
                    set_parts.append(f"{k} = %s")
                    values.append(v)
            if not set_parts:
                return {"success": False, "error": "No valid fields to update"}
            sql = f"UPDATE proyectos SET {', '.join(set_parts)} WHERE id = %s"
            values.append(proyecto_id)
            cursor = self.conn.cursor()
            cursor.execute(sql, tuple(values))
            self.conn.commit()
            affected = cursor.rowcount
            if affected == 0:
                return {"success": False, "error": "Proyecto not found", "id": proyecto_id}
            return {"success": True, "updated_rows": affected}
        except Exception as e:
            self.conn.rollback()
            raise RuntimeError(f"ProyectosDAO update failed: {e}")
        finally:
            if cursor:
                cursor.close()
            if self._owns_connection:
                self.close()

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
                # IMPORTANTE: Para UPDATE/DELETE retornar rowcount, para INSERT retornar lastrowid
                if query.strip().upper().startswith('INSERT'):
                    return cursor.lastrowid
                else:
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
    def delete(self, proyecto_id: int) -> Dict[str, Any]:
        """Elimina un proyecto por ID"""
        try:
            query = "DELETE FROM proyectos WHERE id = %s"
            
            # Usar el método helper _execute_query
            affected_rows = self._execute_query(query, (proyecto_id,), fetch=False)
            
            print(f" Filas afectadas en DELETE: {affected_rows}")
            
            if affected_rows == 0:
                return {"success": False, "error": "Proyecto not found", "id": proyecto_id}
                
            return {"success": True, "deleted_rows": affected_rows}
            
        except Exception as e:
            # No necesitamos rollback aquí porque _execute_query ya lo maneja
            raise RuntimeError(f"ProyectosDAO delete failed: {e}")
    def get_by_fecha(self, fecha: str) -> Dict[str, Any]:
        """
        Devuelve proyectos por fecha específica.
        Útil para filtrar proyectos por fecha.
        """
        cursor = None
        try:
            cursor = self.conn.cursor(pymysql.cursors.DictCursor)
            cursor.execute(
                "SELECT id, nombre, description, imagen, fecha, linkgithub, linkvideo "
                "FROM proyectos WHERE fecha = %s ORDER BY id DESC",
                (fecha,)
            )
            rows = cursor.fetchall()
            return {"success": True, "data": [dict(r) for r in rows]}
        except Exception as e:
            raise RuntimeError(f"ProyectosDAO get_by_fecha failed: {e}")
        finally:
            if cursor:
                cursor.close()
            if self._owns_connection:
                self.close()

    def get_recent_projects(self, limit: int = 10) -> Dict[str, Any]:
        """
        Devuelve los proyectos más recientes.
        Útil para mostrar solo los últimos proyectos en el frontend.
        """
        cursor = None
        try:
            cursor = self.conn.cursor(pymysql.cursors.DictCursor)
            cursor.execute(
                "SELECT id, nombre, description, imagen, fecha, linkgithub, linkvideo "
                "FROM proyectos ORDER BY id DESC LIMIT %s",
                (limit,)
            )
            rows = cursor.fetchall()
            return {"success": True, "data": [dict(r) for r in rows]}
        except Exception as e:
            raise RuntimeError(f"ProyectosDAO get_recent_projects failed: {e}")
        finally:
            if cursor:
                cursor.close()
            if self._owns_connection:
                self.close()