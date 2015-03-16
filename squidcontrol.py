#!/usr/bin/env python
# -*- coding: utf-8 -*-


import time
import sys
import ConfigParser
import logging
import logging.config
from classes.daemon import Daemon
from classes.Comparador import Comparador

global RUTA_CONFIGURACION

#CONFIGURACION - CONFIGURACION - CONFIGURACION -

RUTA_CONFIGURACION = "/etc/squidban.cfg"

#FIN CONFIGURACION - FIN CONFIGURACION - FIN CONFIGURACION -

class SquidControl(Daemon):
    def run(self):
        self.readConfig()
        self.prepareLogging()
        self.logger.info("Iniciando aplicacion")

        try:
            comparador = Comparador(self.accesslog, self.accessloghistoricos, self.ipallowed, self.dnsallowed, self.dbfile)
            contador = 0
            while True:
                contador +=1
                comparador.registrar(self.escanearhistoricos)
                comparador.persistir(self.dbfile)
                if contador >= 10:
                    contador = 0
                    self.logger.info("Actualizando reporte")
                    comparador.reporte()
                time.sleep(self.register_interval)
        except:
            self.logger.exception("Ha ocurrido una excepcion inesperada")

    def readConfig(self, config_file="config.cfg"):
        try:
            config = ConfigParser.ConfigParser()
            config.read([RUTA_CONFIGURACION])
            #Paths
            self.accesslog = config.get("Paths","accesslog")
            self.accessloghistoricos = config.get("Paths","accesslog_historicos")

            self.ipallowed = config.get("Paths","ipallowed").strip().split(",") #ojo que es una lista
            self.dnsallowed = config.get("Paths","dnsallowed").strip().split(",") #ojo que es una lista
            self.rta_ip_baneados = config.get("Paths","ip_baneados").strip()
            self.rta_dns_baneadas = config.get("Paths","dns_baneadas").strip()

            self.dbfile = config.get("Paths","dbfile")
            self.logconfig = config.get("Paths","logconfig", "")
            #Settings
            self.escanearhistoricos = config.get("Settings","escanear_historicos")

            #Times
            self.register_interval = int(config.get("Times","intervalo_de_registro"))
            self.max_inactivity = int(config.get("Times","tiempo_inactividad_usuario"))
        except:
            sys.stderr.write("No fue posible leer archivo de configuracion {}".format(config_file))
            raise

    def prepareLogging(self):
        try:
            logging.config.fileConfig(self.logconfig)
            self.logger = logging.getLogger(__name__)
        except:
            sys.stderr.write("No fue posible leer archivo de configuracion {}".format(self.logconfig))
            raise

    def stop(self):
        self.readConfig()
        self.prepareLogging()
        self.logger.warn("Deteniendo aplicacion")
        Daemon.stop(self)

    def restart(self):
        self.logger.warn("Reiniciando aplicacion")
        self.stop()
        self.run()

if __name__=="__main__":
        s = SquidControl('/tmp/s.pid')
        s.run()

