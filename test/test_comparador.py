# -*- coding: utf-8 -*-
from testify import *

import sys
sys.path.append('..')


from classes.Comparador import Comparador


class TestComparador(TestCase):
    """Test de instanciacion"""

    @class_setup
    def setUp(self):
        """"""

        self.config_comparador = {
            'accesslog': "access.log",
            'accesslog_historicos': ".",
            'ipallowed': ["ip_habilitadas.txt"],
            'dnsallowed': ["dns_habilitadas.txt"],
            'dbfile': "/tmp/db.tests",
            'rta_ip_baneados': "/tmp/ip_test",
            'rta_dns_baneadas': "/tmp/ip_test",
            }

    def test_unico(self):
        "correr test"

        comparador = Comparador(self.config_comparador)
        assert_isinstance(comparador, Comparador)


if __name__ == '__main__':
    run()

