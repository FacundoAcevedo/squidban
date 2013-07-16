#!/usr/bin/env python
# -*- coding: utf-8 -*-


import time
import sys
import ConfigParser
import logging
import logging.config
from classes.daemon import Daemon
from classes.Comparador import Comparador

class SquidControl(Daemon):
  def run(self):
      self.readConfig()
      self.prepareLogging()
      self.logger.info("Iniciando aplicacion")
      
      try:
		comparador = Comparador(self.accesslog, self.ipallowed, self.dbfile)
		while True:
		    comparador.registrar()
		    comparador.persistir(self.dbfile)
		    time.sleep(self.register_interval)
	  except:
			 self.logger.exception("Ha ocurrido una excepcion inesperada")
	 
  def readConfig(self, config_file="config.cfg"):
    try:
      config = ConfigParser.ConfigParser()
      config.read(["config.cfg"])
      self.accesslog = config.get("Paths","accesslog")
      self.ipallowed = config.get("Paths","ipallowed")
      self.dbfile = config.get("Paths","dbfile")
      self.logconfig = config.get("Paths","logconfig", "")
      self.register_interval = int(config.get("Times","register_interval"))
      self.max_inactivity = int(config.get("Times","max_inactivity"))
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
    
if __name__=="__main__":
  s = SquidControl('/tmp/s.pid')
  s.run()
