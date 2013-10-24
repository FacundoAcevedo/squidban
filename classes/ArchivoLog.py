from Archivo import Archivo
from Registro import Registro
import logging
import glob
import gzip
import os

class ArchivoLog(Archivo):
   """Lee y administra los archivos de log"""
   def __init__(self, path, path_historico):
     Archivo.__init__(self, path)
     self.logger = logging.getLogger(__name__)
     self.path = path
     self.accesos = {}
     self.ultimo=0
     self.path_historico = path_historico

   def load(self):
     self.load_historico()
     try:
        with open(self.path, "r") as f:
            filas = list(f)
            cantidad = len(filas) - self.ultimo
            if cantidad > 0:
                for f in filas[self.ultimo:]:
                    linea = f.split() # contenido linea
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

   def load_historico(self):
       """Carga los dos tipos de historicos"""

       #Filtro los archivos del estilo: access.log.N
       listaLogsHistoricos = glob.glob(self.path_historico+'/access.log.*')
       self._load_logs_historicos(listaLogsHistoricos)

       listaGzHistoricos = glob.glob(self.path_historico+'/access.log-*.gz')
       self._load_gz_historicos(listaGzHistoricos)

   def _load_logs_historicos(self, listadoArchivos):
       """Verifico los logs  historicos"""
       for logHistorico in listadoArchivos:
           if not self._log_ya_revisado(logHistorico):
               print "Entre"
               with open(logHistorico, 'r') as f:
                   filas = list(f)
                   cantidad = len(filas) - self.ultimo
                   if cantidad > 0:
                       for f in filas[self.ultimo:]:
                           linea = f.split() # contenido linea
                           if not self.accesos.has_key(linea[2]):
                             register = Registro()
                             register.ip = linea[2]
                             register.time = float(linea[0])
                             self.accesos[register.ip] = register

                           else:
                             #Actualizo la fecha, si es mas actual
                             registro = self.accesos[linea[2]]
                             fechaEnObjeto = registro.time
                             fechaEnLog = float(linea[0])
                             if fechaEnObjeto < fechaEnLog:
                                 registro.time = fechaEnLog

                       self.logger.info("Se han registrado %d nuevos registros", cantidad)
                       self.ultimo += cantidad
               self._marcar_como_revisado(logHistorico)

   def _load_gz_historicos(self, listadoArchivos):
       """Verifico los logs  historicos"""
       for logHistorico in listadoArchivos:
           if not self._log_ya_revisado(logHistorico):
               comprimido = gzip.open(logHistorico, "r")
               filas = list(comprimido.read())
               cantidad = len(filas) - self.ultimo
               if cantidad > 0:
                   for f in filas[self.ultimo:]:
                       linea = f.split() # contenido linea
                       if not self.accesos.hasa_key(linea[2]):
                         register = Registro()
                         register.ip = linea[2]
                         register.time = float(linea[0])
                         self.accesos[register.ip] = register

                       else:
                         #Actualizo la fecha, si es mas actual
                         registro = self.accesos(linea[2])
                         fechaEnObjeto = registro.time
                         fechaEnLog = float(linea[0])
                         if fechaEnObjeto < fechaEnLog:
                             registro.time = fechaEnLog

                   self.logger.info("Se han registrado %d nuevos registros", cantidad)
                   self.ultimo += cantidad
               self._marcar_como_revisado(logHistorico)
               gzip.close()


   def _log_ya_revisado(self, logHistorico):
    self._touch("/tmp/__logs_revisados.log")
    with open("/tmp/__logs_revisados.log", 'r+') as f:
        if logHistorico in list(f):
            return True
        return False

   def _marcar_como_revisado(self, logHistorico):
    """Marco el log como ya revisado"""
    self._touch("/tmp/__logs_revisados.log")
    with open("/tmp/__logs_revisados.log", 'a') as f:
      f.write(logHistorico)


   def get(self,id):
     return self.accesos[id]


   def _touch(self,fname):
     if os.path.exists(fname):
         os.utime(fname, None)
     else:
         open(fname, 'w').close()
