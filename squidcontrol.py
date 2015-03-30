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

# CONFIGURACION - CONFIGURACION - CONFIGURACION -

RUTA_CONFIGURACION = "/etc/squidban.cfg"

# FIN CONFIGURACION - FIN CONFIGURACION - FIN CONFIGURACION -


class SquidControl(Daemon):
    """Clase de control del demonio de squidban"""

    def run(self):
        """Corre squidban en modo demonio"""
        self.readConfig()
        self.prepareLogging()
        self.logger.info("Iniciando aplicacion")
        self.prepararConfig()
        try:
            comparador = Comparador(self.config_comparador)
            contador = 0
            while True:
                contador += 1
                comparador.registrar(self.escanearhistoricos)
                comparador.persistir(self.dbfile)
                if contador >= 10:
                    contador = 0
                    self.logger.info("Actualizando reporte")
                    comparador.reporte()
                time.sleep(self.register_interval)
        except:
            self.logger.exception("Ha ocurrido una excepcion inesperada")

    def runalone(self):
        """Corre squidban bajo demanda, no demonizado."""
        self.readConfig()
        self.prepareLogging()
        self.logger.info("Iniciando aplicacion")
        self.prepararConfig()

        try:
            comparador = Comparador(self.config_comparador)
            comparador.registrar(self.escanearhistoricos)
            comparador.persistir(self.dbfile)

            self.logger.info("Actualizando reporte")
            comparador.reporte()
        except:
            self.logger.exception("Ha ocurrido una excepcion inesperada")

    def prepararConfig(self):
        """Prepara la configuracion"""

        self.config_comparador = {
            'accesslog': self.accesslog,
            'accesslog_historicos': self.accessloghistoricos,
            'ipallowed': self.ipallowed,
            'dnsallowed': self.dnsallowed,
            'dbfile': self.dbfile,
            'rta_ip_baneados': self.rta_ip_baneados,
            'rta_dns_baneadas': self.rta_dns_baneadas,
            }

    def readConfig(self, config_file="config.cfg"):
        """Carga la configuracuion"""
        try:
            config = ConfigParser.ConfigParser()
            config.read([RUTA_CONFIGURACION])
            # Paths
            self.accesslog = config.get("Paths", "accesslog")
            self.accessloghistoricos = config.get("Paths",
                    "accesslog_historicos")
            # lista
            self.ipallowed = config.get("Paths",
                    "ipallowed").strip().split(",")
            # lista
            self.dnsallowed = config.get("Paths",
                    "dnsallowed").strip().split(",")
            self.rta_ip_baneados = config.get("Paths", "ip_baneados").strip()
            self.rta_dns_baneadas = config.get("Paths", "dns_baneadas").strip()

            self.dbfile = config.get("Paths", "dbfile")
            self.logconfig = config.get("Paths", "logconfig", "")
            # Settings
            self.escanearhistoricos = config.get("Settings",
                    "escanear_historicos")

            # Times
            self.register_interval = int(config.get("Times",
                "intervalo_de_registro"))
            self.max_inactivity = int(config.get("Times",
                "tiempo_inactividad_usuario"))
        except:
            sys.stderr.write("No fue posible leer archivo de configuracion {}"
                .format(config_file))
            raise

    def prepareLogging(self):
        """Prepara el logger"""
        try:
            logging.config.fileConfig(self.logconfig)
            self.logger = logging.getLogger(__name__)
        except:
            sys.stderr.write("No fue posible leer archivo de configuracion {}"
                .format(self.logconfig))
            raise

    def stop(self):
        """Finaliza el demonio"""
        self.readConfig()
        self.prepareLogging()
        self.logger.warn("Deteniendo aplicacion")
        Daemon.stop(self)

    def restart(self):
        """Reinicia el demonio"""
        self.logger.warn("Reiniciando aplicacion")
        self.stop()
        self.run()

    def start(self):
        """Inicia el Squidban"""
        s = SquidControl('/tmp/s.pid')
        s.run()

if __name__ == "__main__":
        s = SquidControl('/tmp/s.pid')
        s.runalone()

