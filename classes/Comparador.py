# -*- coding: utf-8 -*-


from ArchivoIP import ArchivoIP
from ArchivoDns import ArchivoDNS
from ArchivoLog import ArchivoLog
from Registro import Registro
from Constantes import IPINVALIDA
import time
import logging
import csv
import cPickle


class Comparador:
    """Compara las entradas de dos archivos"""

    def __init__(self, config_comparador):
        """Constructor
        config_comparador: diccionario con las variables para configurar
            el comparador"""
        # Contador de ejecuciones para el modo demonio
        self.contador_ejecuciones = 0

        #Logs de actividad
        self.logger = logging.getLogger(__name__)
        self.logFile = ArchivoLog(config_comparador["accesslog"],
            config_comparador["accesslog_historicos"])

        #Levanto las rutas de los baneados
        self.rutaDnsBaneados = config_comparador["rta_dns_baneadas"]
        self.rutaIpBaneados = config_comparador["rta_ip_baneados"]

        #Creo los archivos de salida si no existen
        ArchivoIP._touch(self.rutaDnsBaneados)
        ArchivoIP._touch(self.rutaIpBaneados)

        self.listadoIpaddrBaneadas = []
        self.listadoDnsaddrBaneadas = []

        # Cargo las rutas de los  archivos del ipaddr/dnsaddr
        self.ipaddrFile = []
        for ipaddrFile in config_comparador["ipallowed"]:
            self.ipaddrFile.append(ArchivoIP(ipaddrFile))

        self.dnsaddrFile = []
        for dnsaddrFile in config_comparador["dnsallowed"]:
            self.dnsaddrFile.append(ArchivoDNS(dnsaddrFile))

        # Cargo la ruta de la db
        self.dbfile = config_comparador["dbfile"]
        self.cargar()

        # Cargo los archivos de ipaddr/dnsaddr y configuro el objeto
        for ipaddrF in self.ipaddrFile:
            ipaddrF.load()
        for dnsaddrF in self.dnsaddrFile:
            dnsaddrF.load()

    def registrar(self, procesarHistorico=False):
        """Registra los accesos del accesslog"""
        self.contador_ejecuciones += 1

        # Cargo el archivo del log
        if procesarHistorico is True:
            self.logFile.load_historico()
        # Cargo las entradas del log de squid
        self.logFile.load()

        # Contador para el modo demonio
        if self.contador_ejecuciones == 10:
            self.contador_ejecuciones = 0
            self.logger.debug("Registrando cambios")

        # Cargo los accesos
        for acceso in self.logFile.accesos.values():
            usuario = Registro()
            usuario.ip = acceso.ip
            usuario.time = acceso.time
            self.usuarios[usuario.ip] = usuario
            self.cambios = True
            #self.logFile.accesos.clear()

    def revisarIpHabilitadas(self, dias):
        '''Reviso las ip habilitadas comparandolas con sus apariciones
        en el access.log'''
        for ipaddrF in self.ipaddrFile:
            for ip in ipaddrF.usuarios.keys():
                # self.usuarios son las ip del accesslog
                if ip not in self.usuarios or \
                not self.acceso_reciente(self.usuarios[ip].time, dias):
                    usuario = ipaddrF.usuarios[ip]
                    usuario.time = str(self.logFile.getTime(ip))

                    # Genero la linea del csv
                    lineaAGuardar = [usuario.ip, ";" + usuario.time +
                    ";" + usuario.descripcion]

                    self.listadoIpaddrBaneadas.append(lineaAGuardar)

    def revisarDnsHabilitados(self, dias):
        '''Reviso las ip habilitadas comparandolas con sus apariciones
        en el access.log'''
        for dnsaddrF in self.dnsaddrFile:
            for dns in dnsaddrF.usuarios.keys():
                ip = dnsaddrF.usuarios[dns].ip
                if ip not in self.usuarios or not self.acceso_reciente(
                    self.usuarios[ip].time, dias) or ip == IPINVALIDA:
                    usuario = dnsaddrF.usuarios[dns]
                    usuario.time = str(self.logFile.getTime(ip))

                    # Genero la linea del csv
                    lineaAGuardar = [usuario.dns, ";" + usuario.time +
                    ";" + usuario.descripcion]

                    self.listadoDnsaddrBaneadas.append(lineaAGuardar)

    def reporte(self, dias=30):
        """Levanta los csv, actualiza, sincroniza, mergea los cambios con mis
        objetos"""
        self.logger.info("Generando reporte")

        # Reviso las ip habilitadas comparandolas con sus apariciones
        # en el access.log
        self.revisarIpHabilitadas(dias)
        self.revisarDnsHabilitados(dias)

    def reporteGuardar(self):
        """Guarda el reporte a un archivo
        Borra el contenido y lo reescribe"""
        with open(self.rutaDnsBaneados, "wb") as f:
            escritor = csv.writer(f, delimiter=" ")
            for fila in self.listadoDnsaddrBaneadas:
                escritor.writerow(fila)

        with open(self.rutaIpBaneados, "wb") as f:
            escritor = csv.writer(f, delimiter=" ")
            for fila in self.listadoIpaddrBaneadas:
                escritor.writerow(fila)

    def cargar(self):
        """Carga la base de datos y carga los objetos"""
        self.logger.info("Intentado cargar base de datos")
        self.usuarios = {}
        for ipaddrF in self.ipaddrFile:
            ipaddrF.load()
        self.cambios = False
        try:
            with open(self.dbfile, "r") as f:
                self.usuarios = cPickle.load(f)

        except:
            self.logger.warn("No se ha podido acceder a la base de datos \
      en %s, creando una nueva", self.dbfile)
            self.registrar()

    def persistir(self, dbfile):
        """Serializa la db"""
        if self.cambios:
            with open(dbfile, 'wb') as f:
                cPickle.dump(self.usuarios, f, protocol=2)

    def acceso_reciente(self, tiempo_acceso, dias_maximo):
        """True sin accedio recientemente"""
        if tiempo_acceso <= 0:
            return False
        localtime = time.time()
        # paso los dias a segundos
        return localtime - float(tiempo_acceso) < dias_maximo * 24 * 3600

    def utc2string(self, utc):
        """"Transforma utc a string"""
        return time.strftime("%d-%b-%Y %H:%M:%S UTC", time.gmtime(float(utc)))

#Dejo estas funciones por que quizas sean utiles en el futuro
    def banearIpDelAccessLog(self, dias):
        '''Marco como baneadas las ip dentro del accesslog, que no navegan hace
        x dias'''
        for usuario in self.usuarios.values():
            ip = usuario.ip
            # compruebo que la ip no este en la lista de baneados
            if not self.acceso_reciente(usuario.time, dias):
                # esto hace que no pierda el comentario
                if ip not in [x[0] for x in self.listadoIpaddrBaneadas]:
                    lineaAGuardar = [ip, "#"]
                    self.listadoIpaddrBaneadas.append(lineaAGuardar)

    def banearDnsDelAccessLog(self, dias):
        '''Marco como baneadas los dns dentro del accesslog, que no navegan hace
        x dias'''
        for dnsaddrF in self.dnsaddrFile:
            for dns in dnsaddrF.usuarios.keys():
                ip = dnsaddrF.usuarios[dns].ip
                if ip not in self.usuarios or not self.acceso_reciente(
                    self.usuarios[ip].time, dias) or ip == IPINVALIDA:
                    usuario = dnsaddrF.usuarios[dns]
                    # Genero la linea del csv
                    lineaAGuardar = [usuario.dns, "#" + usuario.descripcion]
                    # no lo agrego si es que ya esta
                    if lineaAGuardar not in self.listadoDnsaddrBaneadas:
                        self.listadoDnsaddrBaneadas.append(lineaAGuardar)

    def recargarDnsBaneados(self):
        """Recarga los dns que ya fueron baneados"""
        with open(self.rutaDnsBaneados, "rb")as f:
            lector = csv.reader(f, delimiter=" ")
            for fila in lector:
                if fila not in self.listadoDnsaddrBaneadas:
                    self.listadoDnsaddrBaneadas.append(fila)

    def recargarIpBaneadas(self):
        """Recarga las ip que ya fueron baneados"""
        with open(self.rutaIpBaneados, "rb")as f:
            lector = csv.reader(f, delimiter=" ")
            for fila in lector:
                if fila not in self.listadoIpaddrBaneadas:
                    self.listadoIpaddrBaneadas.append(fila)

# vim: tabstop=4 expandtab shiftwidth=4
