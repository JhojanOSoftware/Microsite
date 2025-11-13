class BaseDAO:
    """
    Simple BaseDAO que otros DAO pueden extender.
    Proporciona manejo básico de cierre de conexión.
    """
    def __init__(self, conn=None):
        self.conn = conn
        self._owns_connection = False if conn else True

    def close(self) -> None:
        """Cerrar la conexión si esta instancia la creó."""
        try:
            if getattr(self, "conn", None) and self._owns_connection:
                try:
                    self.conn.close()
                except Exception:
                    pass
        finally:
            self.conn = None