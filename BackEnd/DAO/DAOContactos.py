from typing import Optional, Dict, Any
from BackEnd.DAO.DAOBase import BaseDAO
from BackEnd.BD_Mysql.ConectorDB import ConectorDB
import pymysql


class ContactosDAO(BaseDAO):
    
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

    def enlistar_contactos(self) -> Dict[str, Any]:
        try:
            query = """
                SELECT id, nombre, telefono, email, mensaje 
                FROM contactos 
                ORDER BY id DESC
            """
            data = self._execute_query(query)
            return {"success": True, "data": data}
        except Exception as e:
            raise RuntimeError(f"ContactosDAO enlistar_contactos failed: {e}")

    def get_by_id(self, contacto_id: int) -> Dict[str, Any]:
        try:
            query = """
                SELECT id, nombre, telefono, email, mensaje 
                FROM contactos 
                WHERE id = %s 
                LIMIT 1
            """
            data = self._execute_query(query, (contacto_id,))
            if not data:
                return {"success": False, "error": "Contacto not found", "id": contacto_id}
            return {"success": True, "data": data[0]}
        except Exception as e:
            raise RuntimeError(f"ContactosDAO get_by_id failed: {e}")

    def create(self, contacto_model) -> Dict[str, Any]:
        try:
            query = """
                INSERT INTO contactos (nombre, telefono, email, mensaje) 
                VALUES (%s, %s, %s, %s)
            """
            values = (
                getattr(contacto_model, "nombre", None),
                getattr(contacto_model, "telefono", None),
                getattr(contacto_model, "email", None),
                getattr(contacto_model, "mensaje", None),
            )
            
            new_id = self._execute_query(query, values, fetch=False)
            
            return {
                "success": True,
                "id": new_id,
                "data": contacto_model.dict() if hasattr(contacto_model, "dict") else dict(contacto_model),
            }
        except Exception as e:
            raise RuntimeError(f"ContactosDAO create failed: {e}")

    def update(self, contacto_id: int, fields: Dict[str, Any]) -> Dict[str, Any]:
        try:
            if not fields:
                return {"success": False, "error": "No fields to update"}
                
            allowed = {"nombre", "telefono", "email", "mensaje"}
            set_parts = []
            values = []
            
            for k, v in fields.items():
                if k in allowed:
                    set_parts.append(f"{k} = %s")
                    values.append(v)
                    
            if not set_parts:
                return {"success": False, "error": "No valid fields to update"}
                
            query = f"UPDATE contactos SET {', '.join(set_parts)} WHERE id = %s"
            values.append(contacto_id)
            
            self._execute_query(query, tuple(values), fetch=False)
            
            return {"success": True, "updated_rows": 1}
        except Exception as e:
            raise RuntimeError(f"ContactosDAO update failed: {e}")

    def delete(self, contacto_id: int) -> Dict[str, Any]:
        try:
            query = "DELETE FROM contactos WHERE id = %s"
            self._execute_query(query, (contacto_id,), fetch=False)
            return {"success": True, "deleted_rows": 1}
        except Exception as e:
            raise RuntimeError(f"ContactosDAO delete failed: {e}")

    def get_by_email(self, email: str) -> Dict[str, Any]:
        try:
            query = """
                SELECT id, nombre, telefono, email, mensaje 
                FROM contactos 
                WHERE email = %s 
                ORDER BY id DESC
            """
            data = self._execute_query(query, (email,))
            return {"success": True, "data": data}
        except Exception as e:
            raise RuntimeError(f"ContactosDAO get_by_email failed: {e}")

    def get_recent_contacts(self, limit: int = 10) -> Dict[str, Any]:
        try:
            query = """
                SELECT id, nombre, telefono, email, mensaje 
                FROM contactos 
                ORDER BY id DESC 
                LIMIT %s
            """
            data = self._execute_query(query, (limit,))
            return {"success": True, "data": data}
        except Exception as e:
            raise RuntimeError(f"ContactosDAO get_recent_contacts failed: {e}")