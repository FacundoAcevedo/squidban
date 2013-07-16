# -*- coding: utf-8 -*-


import csv

class Archivo:
  def __init__(self, path):
    self._path = path
  
  def load(self):
    """Carga el contenido del archivo"""
    pass;
    
  def get(self,id):
    """Obtiene un registro a partir de su identificador"""
    pass;
    
  def import_text(self,filename, separator):
    with open(filename) as f:
      for line in csv.reader(f, delimiter=separator, skipinitialspace=True):
	if line:
	  yield line
