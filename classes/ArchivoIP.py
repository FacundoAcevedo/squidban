# -*- coding: utf-8 -*-


from Archivo import Archivo
from Registro import Registro
import logging

class ArchivoIP(Archivo):
  """Lee y administra los archivos de IP"""
  def __init__(self,path):
     Archivo.__init__(self, path)
     self.logger = logging.getLogger(__name__)
     self.usuarios = {}
   
  def load(self):
    try:
      for linea in self.import_text(self._path, " "):
	register = Registro()
	register.ip = linea[0]
	register.descripcion = linea[1][1:]
	self.usuarios[register.ip] = register
    except:
      self.logger.error("No se ha podido acceder al archivo %s", self.path)
      raise
   
  def get(self,id):
     return self.usuarios[id]
