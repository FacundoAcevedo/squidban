# -*- coding: utf-8 -*-
import csv
import os


class Archivo:
    """Manipulador de ficheros"""
    def __init__(self, path):
        """constructor"""
        self._path = path

    def load(self):
        """Carga el contenido del archivo"""
        pass

    def get(self, id):
        """Obtiene un registro a partir de su identificador"""
        pass

    def import_text(self, filename, separator):
        """Obtener las lineas de un fichero"""
        with open(filename) as f:
            for line in csv.reader(f, delimiter=separator,
                 skipinitialspace=True):
                if line:
                    yield line

    def esComentario(self, linea):
        """Verifica si el primer caracter es #"""
        # Valido la que la linea sea un string
        try:
            linea = " ".join(linea)
        except:
            pass

        if linea.strip()[0] == '#':
            return True
        return False

    @staticmethod
    def _touch(fname):
        """Analogo al touch de linux"""
        if os.path.exists(fname):
            os.utime(fname, None)
        else:
            open(fname, 'w').close()
