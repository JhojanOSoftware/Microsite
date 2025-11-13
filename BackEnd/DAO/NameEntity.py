from typing import Optional, Dict, Any
from BackEnd.DAO.DAOBase import BaseDAO
from BackEnd.BD_Mysql.ConectorDB import ConectorDB
import pymysql


class EntityNameDAO(BaseDAO):
    """
    DAO for 'entity_table'
    Columns:
      - id (PRIMARY KEY)
      - nombre_columna VARCHAR(255)
      - descripcion TEXT
      - activo BOOLEAN
    SQL comments are included in each method where relevant.
    """

    def __init__(self, conn: Optional[pymysql.connections.Connection] = None):
        # If a connection is provided reuse it, otherwise create a new one
        if conn:
            self.conn = conn
            self._owns_connection = False
        else:
            self.conn = ConectorDB().baseConnect()
            self._owns_connection = True

    def close(self) -> None:
        """Close connection if this DAO instance owns it."""
        try:
            if self.conn and self._owns_connection:
                self.conn.close()
        finally:
            self.conn = None

    def list_all(self) -> Dict[str, Any]:
        """
        Devuelve todos los registros ordenados por ID descendente.
        SQL: SELECT id, nombre_columna, descripcion, activo FROM entity_table ORDER BY id DESC;
        """
        cursor = None
        try:
            cursor = self.conn.cursor(pymysql.cursors.DictCursor)
            cursor.execute(
                "SELECT id, nombre_columna, descripcion, activo "
                "FROM entity_table "
                "ORDER BY id DESC"
            )
            rows = cursor.fetchall()
            return {"success": True, "data": [dict(r) for r in rows]}
        except Exception as e:
            raise RuntimeError(f"DAO list_all failed: {e}")
        finally:
            if cursor:
                cursor.close()
            if self._owns_connection:
                self.close()

    def get_by_id(self, entity_id: int) -> Dict[str, Any]:
        """
        Devuelve un registro por su ID.
        SQL: SELECT ... FROM entity_table WHERE id = %s LIMIT 1;
        """
        cursor = None
        try:
            cursor = self.conn.cursor(pymysql.cursors.DictCursor)
            cursor.execute(
                "SELECT id, nombre_columna, descripcion, activo "
                "FROM entity_table WHERE id = %s LIMIT 1",
                (entity_id,),
            )
            row = cursor.fetchone()
            if not row:
                return {"success": False, "error": "Not found", "id": entity_id}
            return {"success": True, "data": dict(row)}
        except Exception as e:
            raise RuntimeError(f"DAO get_by_id failed: {e}")
        finally:
            if cursor:
                cursor.close()
            if self._owns_connection:
                self.close()

    def create(self, entity_model) -> Dict[str, Any]:
        """
        Inserta un nuevo registro en la tabla.
        Parámetro: objeto Pydantic de la entidad (entity_model)
        SQL: INSERT INTO entity_table (nombre_columna, descripcion, activo) VALUES (%s, %s, %s);
        """
        cursor = None
        try:
            cursor = self.conn.cursor()
            sql = (
                "INSERT INTO entity_table (nombre_columna, descripcion, activo) "
                "VALUES (%s, %s, %s)"
            )
            values = (
                getattr(entity_model, "nombre_columna", None),
                getattr(entity_model, "descripcion", None),
                bool(getattr(entity_model, "activo", True)),
            )
            cursor.execute(sql, values)
            self.conn.commit()
            new_id = cursor.lastrowid
            return {"success": True, "id": new_id, "data": entity_model.dict() if hasattr(entity_model, "dict") else dict(entity_model)}
        except Exception as e:
            # onFail: cerrar en finally y lanzar excepción con mensaje claro
            self.conn.rollback()
            raise RuntimeError(f"DAO create failed: {e}")
        finally:
            if cursor:
                cursor.close()
            if self._owns_connection:
                self.close()

    def update(self, entity_id: int, fields: Dict[str, Any]) -> Dict[str, Any]:
        """
        Actualiza los campos de un registro existente por ID.
        fields: diccionario con columnas a actualizar.
        SQL: UPDATE entity_table SET col1=%s, col2=%s WHERE id=%s;
        """
        cursor = None
        try:
            if not fields:
                return {"success": False, "error": "No fields to update"}
            allowed = {"nombre_columna", "descripcion", "activo"}
            set_parts = []
            values = []
            for k, v in fields.items():
                if k in allowed:
                    set_parts.append(f"{k} = %s")
                    values.append(v)
            if not set_parts:
                return {"success": False, "error": "No valid fields to update"}
            sql = f"UPDATE entity_table SET {', '.join(set_parts)} WHERE id = %s"
            values.append(entity_id)
            cursor = self.conn.cursor()
            cursor.execute(sql, tuple(values))
            self.conn.commit()
            affected = cursor.rowcount
            return {"success": True, "updated_rows": affected}
        except Exception as e:
            self.conn.rollback()
            raise RuntimeError(f"DAO update failed: {e}")
        finally:
            if cursor:
                cursor.close()
            if self._owns_connection:
                self.close()

    def delete(self, entity_id: int, logical: bool = True) -> Dict[str, Any]:
        """
        Elimina o desactiva un registro.
        Si 'logical' es True y existe columna 'activo', realiza borrado lógico:
            UPDATE entity_table SET activo = 0 WHERE id = %s;
        Si 'logical' es False realiza DELETE físico.
        """
        cursor = None
        try:
            cursor = self.conn.cursor()
            if logical:
                # prefer logical delete using 'activo' column
                cursor.execute("UPDATE entity_table SET activo = %s WHERE id = %s", (0, entity_id))
            else:
                cursor.execute("DELETE FROM entity_table WHERE id = %s", (entity_id,))
            self.conn.commit()
            affected = cursor.rowcount
            if affected == 0:
                return {"success": False, "error": "Not found", "id": entity_id}
            return {"success": True, "deleted_rows": affected}
        except Exception as e:
            self.conn.rollback()
            raise RuntimeError(f"DAO delete failed: {e}")
        finally:
            if cursor:
                cursor.close()
            if self._owns_connection:
                self.close()



class EntityNameDAO(BaseDAO):
    """
    DAO for 'entity_table'
    Columns:
      - id (PRIMARY KEY)
      - nombre_columna VARCHAR(255)
      - descripcion TEXT
      - activo BOOLEAN
    SQL comments are included in each method where relevant.
    """

    def __init__(self, conn: Optional[pymysql.connections.Connection] = None):
        # If a connection is provided reuse it, otherwise create a new one
        if conn:
            self.conn = conn
            self._owns_connection = False
        else:
            self.conn = ConectorDB().baseConnect()
            self._owns_connection = True

    def close(self) -> None:
        """Close connection if this DAO instance owns it."""
        try:
            if self.conn and self._owns_connection:
                self.conn.close()
        finally:
            self.conn = None

    def list_all(self) -> Dict[str, Any]:
        """
        Devuelve todos los registros ordenados por ID descendente.
        SQL: SELECT id, nombre_columna, descripcion, activo FROM entity_table ORDER BY id DESC;
        """
        cursor = None
        try:
            cursor = self.conn.cursor(pymysql.cursors.DictCursor)
            cursor.execute(
                "SELECT id, nombre_columna, descripcion, activo "
                "FROM entity_table "
                "ORDER BY id DESC"
            )
            rows = cursor.fetchall()
            return {"success": True, "data": [dict(r) for r in rows]}
        except Exception as e:
            raise RuntimeError(f"DAO list_all failed: {e}")
        finally:
            if cursor:
                cursor.close()
            if self._owns_connection:
                self.close()

    def get_by_id(self, entity_id: int) -> Dict[str, Any]:
        """
        Devuelve un registro por su ID.
        SQL: SELECT ... FROM entity_table WHERE id = %s LIMIT 1;
        """
        cursor = None
        try:
            cursor = self.conn.cursor(pymysql.cursors.DictCursor)
            cursor.execute(
                "SELECT id, nombre_columna, descripcion, activo "
                "FROM entity_table WHERE id = %s LIMIT 1",
                (entity_id,),
            )
            row = cursor.fetchone()
            if not row:
                return {"success": False, "error": "Not found", "id": entity_id}
            return {"success": True, "data": dict(row)}
        except Exception as e:
            raise RuntimeError(f"DAO get_by_id failed: {e}")
        finally:
            if cursor:
                cursor.close()
            if self._owns_connection:
                self.close()

    def create(self, entity_model) -> Dict[str, Any]:
        """
        Inserta un nuevo registro en la tabla.
        Parámetro: objeto Pydantic de la entidad (entity_model)
        SQL: INSERT INTO entity_table (nombre_columna, descripcion, activo) VALUES (%s, %s, %s);
        """
        cursor = None
        try:
            cursor = self.conn.cursor()
            sql = (
                "INSERT INTO entity_table (nombre_columna, descripcion, activo) "
                "VALUES (%s, %s, %s)"
            )
            values = (
                getattr(entity_model, "nombre_columna", None),
                getattr(entity_model, "descripcion", None),
                bool(getattr(entity_model, "activo", True)),
            )
            cursor.execute(sql, values)
            self.conn.commit()
            new_id = cursor.lastrowid
            return {"success": True, "id": new_id, "data": entity_model.dict() if hasattr(entity_model, "dict") else dict(entity_model)}
        except Exception as e:
            # onFail: cerrar en finally y lanzar excepción con mensaje claro
            self.conn.rollback()
            raise RuntimeError(f"DAO create failed: {e}")
        finally:
            if cursor:
                cursor.close()
            if self._owns_connection:
                self.close()

    def update(self, entity_id: int, fields: Dict[str, Any]) -> Dict[str, Any]:
        """
        Actualiza los campos de un registro existente por ID.
        fields: diccionario con columnas a actualizar.
        SQL: UPDATE entity_table SET col1=%s, col2=%s WHERE id=%s;
        """
        cursor = None
        try:
            if not fields:
                return {"success": False, "error": "No fields to update"}
            allowed = {"nombre_columna", "descripcion", "activo"}
            set_parts = []
            values = []
            for k, v in fields.items():
                if k in allowed:
                    set_parts.append(f"{k} = %s")
                    values.append(v)
            if not set_parts:
                return {"success": False, "error": "No valid fields to update"}
            sql = f"UPDATE entity_table SET {', '.join(set_parts)} WHERE id = %s"
            values.append(entity_id)
            cursor = self.conn.cursor()
            cursor.execute(sql, tuple(values))
            self.conn.commit()
            affected = cursor.rowcount
            return {"success": True, "updated_rows": affected}
        except Exception as e:
            self.conn.rollback()
            raise RuntimeError(f"DAO update failed: {e}")
        finally:
            if cursor:
                cursor.close()
            if self._owns_connection:
                self.close()

    def delete(self, entity_id: int, logical: bool = True) -> Dict[str, Any]:
        """
        Elimina o desactiva un registro.
        Si 'logical' es True y existe columna 'activo', realiza borrado lógico:
            UPDATE entity_table SET activo = 0 WHERE id = %s;
        Si 'logical' es False realiza DELETE físico.
        """
        cursor = None
        try:
            cursor = self.conn.cursor()
            if logical:
                # prefer logical delete using 'activo' column
                cursor.execute("UPDATE entity_table SET activo = %s WHERE id = %s", (0, entity_id))
            else:
                cursor.execute("DELETE FROM entity_table WHERE id = %s", (entity_id,))
            self.conn.commit()
            affected = cursor.rowcount
            if affected == 0:
                return {"success": False, "error": "Not found", "id": entity_id}
            return {"success": True, "deleted_rows": affected}
        except Exception as e:
            self.conn.rollback()
            raise RuntimeError(f"DAO delete failed: {e}")
        finally:
            if cursor:
                cursor.close()
            if self._owns_connection:
                self.close()