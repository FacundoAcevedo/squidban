from Archivo import Archivo
from Registro import Registro
import logging

class ArchivoLog(Archivo):
   """Lee y administra los archivos de log"""
   def __init__(self, path):
     Archivo.__init__(self, path)
     self.logger = logging.getLogger(__name__)
     self.path = path
     self.accesos = {}
     self.ultimo=0
   
   def load(self):
     try:
	with open(self.path, "r") as f:
	    filas = list(enumerate(f))
	    cantidad = len(filas) - self.ultimo
	    if cantidad > 0:
		for f in filas[self.ultimo:]:
		    linea = f[1].split()
		    register = Registro()
		    register.ip = linea[2]
		    register.time = float(linea[0])
		    self.accesos[register.ip] = register
		self.logger.info("Se han registrado %d nuevos registros", cantidad)
		self.ultimo += cantidad
	    # Verificamos si el squid hizo rotacion de logs
	    elif cantidad < 0: 
		self.ultimo = 0
		self.load()
		
     except IOError:
	self.logger.error("No se ha podido acceder al archivo %s", self.path)
	raise
   
   def get(self,id):
     return self.accesos[id]