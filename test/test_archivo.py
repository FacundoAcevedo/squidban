# -*- coding: utf-8 -*-
# -*- coding: utf-8 -*-
from testify import *

import sys
sys.path.append('..')

from classes.Archivo import Archivo


class TestComparador(TestCase):
    """Test de instanciacion"""

    @class_setup
    def setUp(self):
        """"""
        self.ruta = "ip_habilitadas.txt"
        self.Archivo = Archivo(self.ruta)

    def test_esComentario(self):
        "Verifica la funcion esComentario"
        linea0 = "#100.000.000.1 #asd"
        linea1 = " #100.000.000.1 #asd"
        linea2 = "100.000.000.1 #asd"
        linea3 = ""

        lista_comentada = [linea0, linea1]
        lista_sin_comentar = [linea2, linea3]

        for i in lista_comentada:
            assert_equal(self.Archivo.esComentario(i), True)

        for i in lista_sin_comentar:
            assert_equal(self.Archivo.esComentario(i), False)

if __name__ == '__main__':
    run()
