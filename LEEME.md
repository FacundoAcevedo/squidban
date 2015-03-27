--SquidBan--

--Instalacion:
    Ejecutar bash setup.sh, esto copiara los archivos y dara los permisos necesarios
    sqb se instalara por defecto en /opt/squidban, y la configuracion en
    /etc/squidban.cfg. Tambien se copiara en /etc/init.d/ un script de inicializacion
    del demonio.

--Desinstalacion:
    Hay que modificar setup.sh, y descomentar la llamada a la funcion desinstalar,
    que esta sobre la llamada a instalar.


--Uso:
    service squidban [start,runalone,restart,stop]
    Para correr sin demonizar:
        service squidban runalone
        o directamente python2.7 squidcontrol.py

--Configuracion
    [Paths]
    accesslog: Ruta al accesslog actual de Squid.
    accesslog_historicos: Ruta al directorio con los accesslog historicos.

    ip_baneados: Ruta del archivo donde se guardaran las ip baneadas.
    dns_baneados: Ruta del archivo donde se guardaran los dns baneados.

    ipallowed: Rutas a los ficheros de ip habilitados [separado por coma].
    dnsallowed: Ruta a los ficheros de dns de maquinas habilitadas [separado por coma].

    dbfile: Fichero serializado de la aplicacion Default: /opt/squidban/db
    logconfig: Fichero con la configuracion de log: Default: /opt/squidban/log.conf

    [Settings]
    escanear_historicos: True|False Busca ips y dns en los ficheros historicos de log

    [Times]
    intervalo_de_registro: 2 Tiempo de espera cada 10 ejecuciones
    tiempo_inactividad_usuario: 10 Cantidad de dias que una ip|dns no debe aparecer en los logs para ser baneada

--Nota:

    Para forzar la lectura de todos los logs historicos ( inclusive los comprimidos)
    hay que borrar el archivo /tmp/__logs_revisados.log

    Cuando se reinicia el servicio, se analizara el log actual desde el principio

