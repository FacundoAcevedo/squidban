import sys
import time
import sys
import ConfigParser
import logging
import logging.config
from classes.Comparador import Comparador

class Reporter():
    """Llama al comparador y genera el reporte"""
  def run(self):
      self.readConfig()
      self.prepareLogging()
      self.logger.info("Creando reporte")
      try:
	comparador = Comparador(self.accesslog, self.ipallowed, self.dbfile)
	comparador.reporte(int(sys.argv[1]))
	self.logger.info("Reporte generado con exito")
      except:
	 self.logger.exception("Ha ocurrido una excepcion inesperada")

  def readConfig(self, config_file="config.cfg"):
    try:
      config = ConfigParser.ConfigParser()
      config.read(["config.cfg"])
      self.accesslog = config.get("Paths","accesslog")
      self.ipallowed = config.get("Paths","ipallowed").split(",")
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


if __name__ == "__main__": #TODO Hacerlo demonio
  r = Reporter()
  r.run()
