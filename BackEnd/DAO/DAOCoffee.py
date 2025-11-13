from typing import Optional, Dict, Any
from BackEnd.DAO.DAOBase import BaseDAO
from BackEnd.BD_Mysql.ConectorDB import ConectorDB
import pymysql

class CoffeeDAO(BaseDAO):
    
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

    def enlistarcoffees(self) -> Dict[str, Any]:
        try:
            query = """
                SELECT id, coffee_type, coffe_image, description, video, activo 
                FROM coffee 
                ORDER BY id ASC
            """
            data = self._execute_query(query)
            return {"success": True, "data": data}
        except Exception as e:
            raise RuntimeError(f"CoffeeDAO enlistarcoffees failed: {e}")

    def get_by_id(self, coffee_id: int) -> Dict[str, Any]:
        try:
            query = """
                SELECT id, coffee_type, coffe_image, description, video, activo 
                FROM coffee 
                WHERE id = %s 
                LIMIT 1
            """
            data = self._execute_query(query, (coffee_id,))
            if not data:
                return {"success": False, "error": "Not found", "id": coffee_id}
            return {"success": True, "data": data[0]}
        except Exception as e:
            raise RuntimeError(f"CoffeeDAO get_by_id failed: {e}")

    def create(self, coffee_model) -> Dict[str, Any]:
        try:
            query = """
                INSERT INTO coffee (coffee_type, coffe_image, description, video, activo) 
                VALUES (%s, %s, %s, %s, %s)
            """
            values = (
                getattr(coffee_model, "coffee_type", None),
                getattr(coffee_model, "coffe_image", None),
                getattr(coffee_model, "description", None),
                getattr(coffee_model, "video", None),
                bool(getattr(coffee_model, "activo", True)),
            )
            
            new_id = self._execute_query(query, values, fetch=False)
            
            return {
                "success": True,
                "id": new_id,
                "data": coffee_model.dict() if hasattr(coffee_model, "dict") else dict(coffee_model),
            }
        except Exception as e:
            raise RuntimeError(f"CoffeeDAO create failed: {e}")


    def update_coffee(self, coffee_id: int, fields: Dict[str, Any]) -> Dict[str, Any]:
        #        Actualiza los campos de un registro existente por ID.
        cursor = None
        try:
            if not fields:
                return {"success": False, "error": "No fields to update"}
            allowed = {"coffee_type", "coffe_image", "description", "video", "activo"}
            set_parts = []
            values = []
            for k, v in fields.items():
                if k in allowed:
                    set_parts.append(f"{k} = %s")
                    values.append(v)
            if not set_parts:
                return {"success": False, "error": "No valid fields to update"}
            sql = f"UPDATE coffee SET {', '.join(set_parts)} WHERE id = %s"
            values.append(coffee_id)
            cursor = self.conn.cursor()
            cursor.execute(sql, tuple(values))
            self.conn.commit()
            affected = cursor.rowcount
            return {"success": True, "updated_rows": affected}
        except Exception as e:
            self.conn.rollback()
            raise RuntimeError(f"CoffeeDAO update failed: {e}")
        finally:
            if cursor:
                cursor.close()
            if self._owns_connection:
                self.close()

    def delete_coffee(self, coffee_id: int, logical: bool = True) -> Dict[str, Any]:
        #        Elimina o desactiva un registro.
        cursor = None
        try:
            cursor = self.conn.cursor()
            if logical:
                cursor.execute("UPDATE coffee SET activo = %s WHERE id = %s", (0, coffee_id))
            else:
                cursor.execute("DELETE FROM coffee WHERE id = %s", (coffee_id,))
            self.conn.commit()
            affected = cursor.rowcount
            if affected == 0:
                return {"success": False, "error": "Not found", "id": coffee_id}
            return {"success": True, "deleted_rows": affected}
        except Exception as e:
            self.conn.rollback()
            raise RuntimeError(f"CoffeeDAO delete failed: {e}")
        finally:
            if cursor:
                cursor.close()
            if self._owns_connection:
                self.close()


