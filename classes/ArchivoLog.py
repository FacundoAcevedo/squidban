from Archivo import Archivo
from Registro import Registro
import logging
import glob
import gzip
import os
import cPickle
import subprocess
import sys

class ArchivoLog(Archivo):
   """Lee y administra los archivos de log"""
   def __init__(self, path, path_historico):
     Archivo.__init__(self, path)
     self.logger = logging.getLogger(__name__)
     self.path = path
     self.accesos = {}
     self.ultimo=0
     self.path_historico = path_historico

     self.where = 0
     self.tamano = 9**100


   #@profile
   def load(self):
     #try:
     #   with open(self.path, "r") as f:
     #       self.logger.debug("Revisando log actual")
     #       filas = list(f)
     #       cantidad = len(filas) - self.ultimo
     #       if cantidad > 0:
     #           for f in filas[self.ultimo:]:
     #               linea = f.split() # contenido linea
     #               register = Registro()
     #               register.ip = linea[2]
     #               register.time = float(linea[0])
     #               self.accesos[register.ip] = register
     #           self.logger.info("Se han registrado %d nuevos registros", cantidad)
     #           self.ultimo += cantidad
     #       # Verificamos si el squid hizo rotacion de logs
     #       elif cantidad < 0:
     #           self.ultimo = 0
     #           self.load()

     #Lo mas optimo hasta ahora:
     try:
	#obtengo el tamano del archivo
        tamano = os.stat(self.path)[6]
        with open(self.path, "r") as f:
	        lineas = self._tailf(f, tamano)
            for  f in lineas:
		       if f == "" or not f:
                   del f,lineas
		           break
                linea = f.split() # contenido linea
                register = Registro()
                register.ip = linea[2]
                register.time = float(linea[0])
                self.accesos[register.ip] = register

     except IOError:
        self.logger.error("No se ha podido acceder al archivo %s", self.path)
        raise

   def _tailf(self, file, tamano):
       #si el tamano es menor al que tengo guardado, es que el log roto
       if tamano < self.tamano:
          self.tamano = tamano
          self.where = 0

       salir = False
       file.seek(self.where)
       while True:
	   self.where = file.tell()
           line = file.readline()
           if not line:
               file.seek(self.where)
               del line
	       break
           else:
               yield line

   def load_historico(self):
       """Carga los dos tipos de historicos"""
       self.logger.info("Reviso los historicos")

       #Filtro los archivos del estilo: access.log.N
       listaLogsHistoricos = glob.glob(self.path_historico+'/access.log.*')
       self._load_logs_historicos(listaLogsHistoricos)

       listaGzHistoricos = glob.glob(self.path_historico+'/access.log-*.gz')
       self._load_gz_historicos(listaGzHistoricos)

   def _load_logs_historicos(self, listadoArchivos):
       """Verifico los logs  historicos"""
       for logHistorico in listadoArchivos:
           if not self._log_ya_revisado(logHistorico):
               with open(logHistorico, 'r') as f:
                   filas = list(f)
                   cantidad = len(filas) - self.ultimo
                   if cantidad > 0:
                       self.logger.debug("Revisando %s historicos", logHistorico)
                       for f in filas[self.ultimo:]:
                           linea = f.split() # contenido linea
                           if not self.accesos.has_key(linea[2]):
                             register = Registro()
                             register.ip = linea[2]
                             register.time = float(linea[0])
                             self.accesos[register.ip] = register
                             self.logger.info("Agregando %s a la db", register.ip)

                           else:
                             #Actualizo la fecha, si es mas actual
                             registro = self.accesos[linea[2]]
                             fechaEnObjeto = registro.time
                             fechaEnLog = float(linea[0])
                             if fechaEnObjeto < fechaEnLog:
                                 registro.time = fechaEnLog
                                 self.logger.info("Actualizando aparicion de %s", registro.ip)

                       i#self.logger.info("Se han registrado %d nuevos registros", cantidad)
                       self.ultimo += cantidad
               self._marcar_como_revisado(logHistorico)

   def _load_gz_historicos(self, listadoArchivos):
       """Verifico los logs  historicos"""
       for logHistorico in listadoArchivos:
           if not self._log_ya_revisado(logHistorico):
               comando = ["nice -n 15 /bin/gzip -dc "+logHistorico+" | /bin/awk '{print $1\" \"$3}'"]
               comprimido = subprocess.Popen(comando,shell=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
               resultado = comprimido.communicate()
               stdout = resultado[0] # 1 es stderr
               filas = stdout.split("\n")
               cantidad = len(filas)
               if cantidad > 0:
                   self.logger.debug("Revisando %s historicos", logHistorico)
                   for f in filas:
                       if f:
                           linea = f.split() # contenido linea
                           if not self.accesos.has_key(linea[1]):
                             register = Registro()
                             register.ip = linea[1]
                             register.time = float(linea[0])
                             self.accesos[register.ip] = register
                             self.logger.info("Agregando %s a la db", register.ip)

                           else:
                             #Actualizo la fecha, si es mas actual
                             registro = self.accesos[linea[1]]
                             fechaEnObjeto = registro.time
                             fechaEnLog = float(linea[0])
                             if fechaEnObjeto < fechaEnLog:
                                 registro.time = fechaEnLog
                                 #self.logger.info("Actualizando aparicion de %s", registro.ip)

                   self.logger.info("Se han registrado %d nuevos registros", cantidad)
                   self.logger.info("Se proceso %s completamente.", logHistorico)
               self._marcar_como_revisado(logHistorico)


   def _log_ya_revisado(self, logHistorico):
    self._touch("/tmp/__logs_revisados.log")
    with open("/tmp/__logs_revisados.log", 'r') as f:
        #Si el archivo esta vacio, este try me salva un EOFError
        try:
            procesados = cPickle.load(f)
            if logHistorico in procesados:
                return True
        except:
            return False

   def _marcar_como_revisado(self, logHistorico):
    """Marco el log como ya revisado"""
    self._touch("/tmp/__logs_revisados.log")
    with open("/tmp/__logs_revisados.log", 'rb') as f:
        try:
            procesados = cPickle.load(f)
        except:
            procesados = []
    if logHistorico not in procesados:
        procesados.append(logHistorico)
        with open("/tmp/__logs_revisados.log", 'wb') as f:
           cPickle.dump(procesados, f, protocol=2)


   def get(self,id):
     return self.accesos[id]


