# -*- coding: utf-8 -*-
from testify import *

import sys
sys.path.append('..')

from classes.ArchivoIP import ArchivoIP


class TestArchivoIP(TestCase):
    """Test de instanciacion"""

    @class_setup
    def setUp(self):
        """"""
        self.ruta = "ip_habilitadas.txt"
        self.ArchivoIP = ArchivoIP(self.ruta)

    def test_get_vacio(self):
        "Verifica la inicializacion"
        assert_equals(self.ArchivoIP.get("500.200.500.200"), None)

    def test_carga(self):
        "Test de carga"
        self.ArchivoIP.load()

        assert_not_empty(self.ArchivoIP.usuarios)


if __name__ == '__main__':
    run()