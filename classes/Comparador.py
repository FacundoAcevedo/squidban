# -*- coding: utf-8 -*-


from ArchivoIP import ArchivoIP
from ArchivoDns import ArchivoDNS
from ArchivoLog import ArchivoLog
from Registro import Registro
import time, logging
import csv

class Comparador:
  """Compara las entradas de dos archivos"""
  def __init__(self,logFile, logFilesHistoricos, ipaddrFiles,dnsaddrFiles, dbfile):
    self.logger = logging.getLogger(__name__)
    self.logFile = ArchivoLog(logFile, logFilesHistoricos)

    #Cargo los arguvis del ipaddr
    self.ipaddrFile = []
    for ipaddrFile in ipaddrFiles:
        self.ipaddrFile.append( ArchivoIP(ipaddrFile) )

    self.dnsaddrFile = []
    for dnsaddrFile in dnsaddrFiles:
        self.dnsaddrFile.append( ArchivoDNS(dnsaddrFiles) )

    self.dbfile = dbfile
    self.cargar()

  def registrar(self):
    """Registra los accesos del accesslog"""
    #Cargo el archivo del log
    self.logger.debug("Revisando logs historicos")
    self.logFile.load_historico()
    self.logger.debug("Revisando log actual")
    self.logFile.load()
    #Cargo los archivos de ipaddr y configuro el objeto
    for ipaddrF in self.ipaddrFile:
        ipaddrF.load()
    #self.logger.debug("Registrando cambios")

    #Cargo los accesos
    for acceso in self.logFile.accesos.values():
        usuario = Registro()
        usuario.ip = acceso.ip
        usuario.time = acceso.time
        self.usuarios[usuario.ip] = usuario
        self.logger.debug("%s - %s", self.utc2string(usuario.time), usuario.ip)
        self.cambios = True
        self.logFile.accesos.clear()

  def reporte(self, dias=30):
    self.logger.info("Generando reporte")
    print "IP sin actividad en los ultimos", dias, "dias"
    for ipaddrF in self.ipaddrFile:
        for ip in ipaddrF.usuarios.keys():
            if ip not in self.usuarios or not self.acceso_reciente(self.usuarios[ip].time, dias):
                usuario = ipaddrF.usuarios[ip]
                print usuario.ip

  def cargar(self):
    self.logger.info("Intentado cargar base de datos")
    self.usuarios = {}
    for ipaddrF in self.ipaddrFile:
        ipaddrF.load()
    self.cambios = False
    try:
        with open(self.dbfile, "r") as f:
            for line in csv.reader(f, delimiter='\t', skipinitialspace=True):
                if line:
                    usuario = Registro()
                    usuario.ip = line[0]
                    usuario.time = line[1]
                    self.usuarios[usuario.ip] = usuario
    except (IOError, EOFError):
      self.logger.warn("No se ha podido acceder a la base de datos en %s, creando una nueva", self.dbfile)
      self.registrar()
      pass;

  def persistir(self, dbfile):
    if self.cambios:
        with open(dbfile, 'w') as f:
            writer = csv.writer(f, delimiter='\t')
            for u in self.usuarios.values():
                writer.writerow([u.ip, u.time, self.utc2string(u.time)])
                self.logger.debug("Se han guardado %d registros en la base de datos", len(self.usuarios))
                self.cambios = False

  def acceso_reciente(self, tiempo_acceso, dias_maximo):
    localtime = time.time()
    return localtime - float(tiempo_acceso) < dias_maximo * 24 * 3600 # paso los dias a segundos

  def utc2string(self, utc):
      return time.strftime("%d-%b-%Y %H:%M:%S UTC",time.gmtime(float(utc)))
