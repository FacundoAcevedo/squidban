# -*- coding: utf-8 -*-


from Archivo import Archivo
from Registro import Registro
import logging


class ArchivoIP(Archivo):
    """Lee y administra los archivos de IP"""

    def __init__(self, path):
        """Constructor"""
        Archivo.__init__(self, path)
        self.path = path
        self.logger = logging.getLogger(__name__)
        self.usuarios = {}

    def load(self):
        """Carga las ip del archivo y genera los objetos"""
        try:
            for linea in self.import_text(self._path, " "):
                # Verifico si es un comentario
                if not self.esComentario(linea):
                    register = Registro()
                    register.ip = str(linea[0]).strip()
                    # Verifico si tiene comentarios a derecha y los guardo
                    if len(linea) >= 2:
                        register.descripcion = linea[1][1:]
                    else:
                        register.descripcion = ""

                    # 0.0 significa que nunca se conecto
                    register.time = "0.0"
                    self.usuarios[register.ip] = register

        except:
            self.logger.error("No se ha podido acceder \
            al archivo %s", self.path)
            raise

    def get(self, id):
        """Obtiene el usuario segun id"""
        try:
            return self.usuarios[id]
        except KeyError:
            return None
