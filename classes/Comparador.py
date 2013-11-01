# -*- coding: utf-8 -*-


from ArchivoIP import ArchivoIP
from ArchivoDns import ArchivoDNS
from ArchivoLog import ArchivoLog
from Registro import Registro
import time, logging
import csv
import cPickle

class Comparador:
  """Compara las entradas de dos archivos"""
  def __init__(self,logFile, logFilesHistoricos, ipaddrFiles,dnsaddrFiles, dbfile):
    self.logger = logging.getLogger(__name__)
    self.logFile = ArchivoLog(logFile, logFilesHistoricos)

    self.rutaDnsBaneados= "/tmp/dnsbaneados"
    self.rutaIpBaneados= "/tmp/ipbaneados"
    ArchivoIP._touch(self.rutaDnsBaneados)
    ArchivoIP._touch(self.rutaIpBaneados)
    self.listadoIpaddrBaneadas = []
    self.listadoDnsaddrBaneadas = []

    #Cargo los arguvis del ipaddr
    self.ipaddrFile = []
    for ipaddrFile in ipaddrFiles:
        print ipaddrFile
        self.ipaddrFile.append( ArchivoIP(ipaddrFile) )

    self.dnsaddrFile = []
    for dnsaddrFile in dnsaddrFiles:
        self.dnsaddrFile.append( ArchivoDNS(dnsaddrFile) )

    self.dbfile = dbfile
    self.cargar()
    #Cargo los archivos de ipaddr y configuro el objeto
    for ipaddrF in self.ipaddrFile:
        ipaddrF.load()
    for dnsaddrF in self.dnsaddrFile:
        dnsaddrF.load()


  def registrar(self):
    """Registra los accesos del accesslog"""
    #Cargo el archivo del log
    self.logFile.load_historico()
    self.logFile.load()
    self.logger.debug("Registrando cambios")

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

    #Levanto los csv y actualizo sincronizo mergeo los cambios con mis objetos
    with open(self.rutaDnsBaneados, "rb")as f:
        lector = csv.reader(f, delimiter=" ")
        for fila in lector:
            if fila not in self.listadoDnsaddrBaneadas:
                self.listadoDnsaddrBaneadas.append(fila)

    #Levanto las ip ya benadas
    with open(self.rutaIpBaneados, "rb")as f:
        lector = csv.reader(f, delimiter=" ")
        for fila in lector:
            if fila not in self.listadoIpaddrBaneadas:
                self.listadoIpaddrBaneadas.append(fila)


    #Lo hago antes que sobre el access.log para mantener los comentarios
    #y no sobreescribirlo
    for ipaddrF in self.ipaddrFile:
        for ip in ipaddrF.usuarios.keys():
            if ip not in self.usuarios or not self.acceso_reciente(self.usuarios[ip].time, dias):
                usuario = ipaddrF.usuarios[ip]
                #Genero la linea del csv
                if ip not in [x[0]  for x in  self.listadoIpaddrBaneadas]:
                    lineaAGuardar = [usuario.ip,"#"+usuario.descripcion]
                    self.listadoIpaddrBaneadas.append(lineaAGuardar)

    #Baneo las del access.log
    for usuario in self.usuarios.values():
        ip = usuario.ip
        if not self.acceso_reciente(usuario.time, dias):
            #compruebo que la ip no este en la lista de baneados
            if ip not in [x[0]  for x in  self.listadoIpaddrBaneadas]:
                print ip
                lineaAGuardar = [ip,"#"]
                self.listadoIpaddrBaneadas.append(lineaAGuardar)


    for dnsaddrF in self.dnsaddrFile:
        for dns in dnsaddrF.usuarios.keys():
            ip = dnsaddrF.usuarios[dns].ip
            if ip not in self.usuarios or not self.acceso_reciente(self.usuarios[ip].time, dias) or ip == "666.666.666.666":
                usuario = dnsaddrF.usuarios[dns]
                #Genero la linea del csv
                lineaAGuardar = [usuario.dns,"#"+usuario.descripcion]
                #no lo agrego si es que ya esta
                if lineaAGuardar not in self.listadoDnsaddrBaneadas:
                    self.listadoDnsaddrBaneadas.append(lineaAGuardar)

#    #Quito las ip que estan de mas. OPTIMIZABLE
#    ipRecuperadas = []
#    for sublista in self.listadoIpaddrBaneadas:
#        ip = sublista[0]
#        if ip not in self.usuarios or  not self.acceso_reciente(self.usuarios[ip].time, dias):
#            ipRecuperadas.append(sublista)
#    for sublista in ipRecuperadas:
#        self.listadoIpaddrBaneadas.remove(sublista)
#
#    dnsRecuperadas = []
#    for sublista in self.listadoDnsaddrBaneadas:
#        if dnsaddrF.usuarios.has_key(sublista[0]):
#            ip = dnsaddrF.usuarios[sublista[0]].ip
#            if ip not in self.usuarios or  not self.acceso_reciente(self.usuarios[ip].time, dias):
#                dnsRecuperadas.append(sublista)
#    for sublista in dnsRecuperadas:
#        self.listadoDnsaddrBaneadas.remove(sublista)

    with open(self.rutaDnsBaneados, "wb") as f:
        escritor = csv.writer(f, delimiter=" ")
        for fila in self.listadoDnsaddrBaneadas:
                escritor.writerow(fila)

    with open(self.rutaIpBaneados, "wb") as f:
        escritor = csv.writer(f, delimiter=" ")
        for fila in self.listadoIpaddrBaneadas:
            #if not self.acceso_reciente(self.usuarios[fila[0]].time, dias):
            escritor.writerow(fila)

  def cargar(self):
    self.logger.info("Intentado cargar base de datos")
    self.usuarios = {}
    for ipaddrF in self.ipaddrFile:
        ipaddrF.load()
    self.cambios = False
    try:
        with open(self.dbfile, "r") as f:
            self.usuarios = cPickle.load(f)

    except:
      self.logger.warn("No se ha podido acceder a la base de datos en %s, creando una nueva", self.dbfile)
      self.registrar()
      pass;

  def persistir(self, dbfile):

    #Serializo el objeto
    if self.cambios:
        with open(dbfile, 'wb') as f:
            cPickle.dump(self.usuarios, f, protocol=2)

  def acceso_reciente(self, tiempo_acceso, dias_maximo):
    if tiempo_acceso <= 0:
        return False
    localtime = time.time()
    return localtime - float(tiempo_acceso) < dias_maximo * 24 * 3600 # paso los dias a segundos

  def utc2string(self, utc):
      return time.strftime("%d-%b-%Y %H:%M:%S UTC",time.gmtime(float(utc)))
