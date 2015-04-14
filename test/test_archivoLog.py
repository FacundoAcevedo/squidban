# -*- coding: utf-8 -*-
from testify import *

import sys
sys.path.append('..')
import os
from classes.ArchivoLog import ArchivoLog


class  TestArchivoLog_load(TestCase):
    """Testea ArchivoLog load"""

    @class_setup
    def setUp(self):
        """setup"""
        ruta_al_log = "access.log"
        ruta_historicos = "."

        self.archivo_log = ArchivoLog(ruta_al_log, ruta_historicos)

    def test_load(self):
        """Verificacion de atributos"""
        self.archivo_log.load()

        assert_not_empty(self.archivo_log.accesos)

    def test_load_fichero_vacio(self):
        "Fichero vacio"

        self.archivo_log.path = "access.log_vacio"

        assert_empty(self.archivo_log.accesos)

    def test_load_fichero_inexistente(self):
        "IOError al cargar fichero que no existe"

        self.archivo_log.path = "NeExiSto.TxT"

        assert_raises(OSError, self.archivo_log.load)


class  TestArchivoLog_getTime(TestCase):
    """Testea ArchivoLog getTime"""

    @class_setup
    def setUp(self):
        """setup"""
        ruta_al_log = "access.log"
        ruta_historicos = "."
        self.archivo_log = ArchivoLog(ruta_al_log, ruta_historicos)
        self.archivo_log.load()

    def test_ip_no_listada(self):
        "Ip que no esta en la lista"
        ip = "255.255.255.255"

        assert_equal("0.0", self.archivo_log.getTime(ip))

    def test_ip_listada(self):
        "Ip que no esta en la lista"
        ip = "1.0.0.1"

        assert_equal(1428422260.276, self.archivo_log.getTime(ip))


class  TestArchivoLog_tailf(TestCase):
    """Testea ArchivoLog getTime"""

    @class_setup
    def setUp(self):
        """setup"""
        ruta_al_log = "access.log"
        ruta_historicos = "."
        self.archivo_log = ArchivoLog(ruta_al_log, ruta_historicos)

        self.temporal = "Test_archivo_log_tailf.temporal"

    @setup
    def crear_archivo(self):
        "Creo el fichero por cada test"
        open(self.temporal, 'w').close()

    @teardown
    def borrar_temporal(self):
        "Borro el fichero temporal al final de cada test de esta clase"
        os.remove(self.temporal)

    def test_fichero_vacio(self):
        "Test si el fichero esta vacio"

        tamano = os.stat(self.temporal)[6]
        # Creo el archivo
        with open(self.temporal, "r") as fichero:
            lineas = self.archivo_log._tailf(fichero, tamano)
            lista_lineas = []
            for i in lineas:
                lista_lineas.append(i)
            assert_empty(lista_lineas)


class TestArchivoLog_load_historico(TestCase):
    """Testea ArchivoLog  load_historico"""

    @class_setup
    def setUp(self):
        """"setup"""
        ruta_al_log = "access.log"
        ruta_historicos = "."
        self.archivo_log = ArchivoLog(ruta_al_log, ruta_historicos)

    def test_historicos_texto_plano(self):
        """Test de carga solo de ficheros en texto plano"""
        ruta_historicos = "./logs_historicos/planos/"
        self.archivo_log.path_historico = ruta_historicos

        self.archivo_log.load_historico(False)
        assert_not_empty(self.archivo_log.accesos)

    def test_historicos_texto_plano_verificacion(self):
        """Verifico las ip cargadas"""

    def test_historicos_comprimidos(self):
        """Test de carga solo de ficheros en texto plano"""
        ruta_historicos = "./logs_historicos/comprimidos/"
        self.archivo_log.path_historico = ruta_historicos

        self.archivo_log.load_historico(False)
        assert_not_empty(self.archivo_log.accesos)

    def test_historicos_mix(self):
        """Test de carga de logs en plano y comprimidos"""
        ruta_historicos_mix = "./logs_historicos/mix/"
        self.archivo_log.path_historico = ruta_historicos_mix

        self.archivo_log.load_historico(False)
        assert_not_empty(self.archivo_log.accesos)


if __name__ == '__main__':
    run()