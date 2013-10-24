# -*- coding: utf-8 -*-


from Archivo import Archivo
from Registro import Registro
import logging

from socket import gethostbyname

class ArchivoDNS(Archivo):
  """Lee y administra los archivos de DNS"""
  def __init__(self,path):
     Archivo.__init__(self, path)
     self.logger = logging.getLogger(__name__)
     self.usuarios = {}

  def load(self):
    try:
      for linea in self.import_text(self._path, " "):
          if not __esComentario(linea):
            register = Registro()
            register.dns = linea[0]
            register.descripcion = linea[1][1:]
            self.usuarios[register.dns] = register
            #Resuelvo el dns
            register.ip = __resolverDns(linea[0])
    except:
      self.logger.error("No se ha podido acceder al archivo %s", self.path)
      raise

  def get(self,id):
     return self.usuarios[id]

  def __resolverDns(self, unDns):
     """Devuelve la ip asociada al dns"""
     try:
       ip = gethostbyname(str(unDns))
       return str(ip)
     except:
       self.logger.warning("No se pudo resolver: "+str(lineaPartida[0]))
       return "666.666.666.666"

