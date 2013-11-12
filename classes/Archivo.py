# -*- coding: utf-8 -*-
import os

class Archivo:
  def __init__(self, path):
    self._path = path

  def load(self):
    """Carga el contenido del archivo"""
    pass;

  def get(self,id):
    """Obtiene un registro a partir de su identificador"""
    pass;

 # def import_text(self,filename, separator):
 #   with open(filename) as f:
 #     for line in csv.reader(f, delimiter=separator, skipinitialspace=True):
 #           if line:
 #             yield line
  def import_text(self,filename, separator):
    with open(filename) as f:
      for linea in f:
          if linea:
              yield linea.split(separator)

  def esComentario(self, linea):
    if linea[0] == '#':
      return True
    return False

  @staticmethod
  def _touch(fname):
    if os.path.exists(fname):
        os.utime(fname, None)
    else:
        open(fname, 'w').close()
