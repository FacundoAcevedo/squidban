    # -*- coding: utf-8 -*-


from Archivo import Archivo
from Registro import Registro
from Constantes import IPINVALIDA
import logging

from socket import gethostbyname


class ArchivoDNS(Archivo):
    """Lee y administra los archivos de DNS"""
    def __init__(self, path):
        """Constructor"""
        Archivo.__init__(self, path)
        self.path = path
        self.logger = logging.getLogger(__name__)
        self.usuarios = {}

    def load(self):
        """Carga genera los objetos pertinentes, y resuelve los dns"""
        try:
            for linea in self.import_text(self._path, " "):
                if not self.esComentario(linea) and linea:
                    register = Registro()
                    register.dns = linea[0]
                    if len(linea) >= 2:
                        register.descripcion = linea[1][1:]
                    else:
                        register.descripcion = ""
                    # Resuelvo el dns
                    register.ip = self._resolverDns(linea[0])

                    # 0.0 significa que nunca se conecto
                    register.time = "0.0"
                    self.usuarios[register.dns] = register
        except:
            self.logger.error("No se ha podido acceder al\
            archivo % s", self.path)
            raise

    def get(self, id):
        """Devuelve el usuario segun id"""
        return self.usuarios[id]

    def ip(self, dns):
        """Devuelve la ip segun dns"""
        return self.usuarios[dns].ip

    def _resolverDns(self, unDns):
        """Devuelve la ip asociada al dns"""
        try:
            ip = gethostbyname(str(unDns))
            return str(ip)
        except:
            self.logger.warning("No se pudo resolver: " + str(unDns))
            return IPINVALIDA
