#! /bin/bash
#
# setup.sh
# copyleft (>) 2013 Facundo M. Acevedo <facevedo[AT]csjn[DOT]com[DOT]ar>
#
# Distributed under terms of the GPLv3+ license.
#


#Copio squidban donde corresponde ^.^

RUTA_INSTALACION="/opt/squidban"

instalar(){

    verificar_python
    copiar_archivos

    
}

desinstalar(){
    borrar_archivos
}

borrar_archivos(){
    echo "Desinstalando SquidBan"
    c=0
    #Borro los archivos
    rm -rf $RUTA_INSTALACION
    res=$?
    echo -n "[$c] Borrando archivos: "
    [ $res -eq 0 ] && echo "OK" || echo "ERROR"
    c=$(($c+1))

    #Borro configuracion
    rm -f  /etc/squidban.cfg
    res=$?
    echo -n "[$c] Borrando configuracion, en /etc/squidban.cfg: "
    [ $res -eq 0 ] && echo "OK" || echo "ERROR"
    c=$(($c+1))

    #Borro el script de inicializacion 
    rm -rf /etc/init.d/squidban 
    res=$?
    echo -n "[$c] Borrando script de lanzamiento en /etc/init.d/: "
    [ $res -eq 0 ] && echo "OK" || echo "ERROR"
    c=$(($c+1))

    #Borro el link 
    rm -rf "/usr/sbin/squidban" 
    res=$?
    echo -n "[$c] Borrando el enlace a /usr/sbin/squidban: "
    [ $res -eq 0 ] && echo "OK" || echo "ERROR"
    c=$(($c+1))
    

}
copiar_archivos(){
    c=0
    echo "Instalando SquidBan en $RUTA_INSTALACION"
    mkdir -p $RUTA_INSTALACION

    #Copio los archivos
    cp -rf squidcontrol.py  sc.py log.conf classes $RUTA_INSTALACION
    res=$?
    echo -n "[$c] Copiando archivos: "
    [ $res -eq 0 ] && echo "OK" || echo "ERROR"
    c=$(($c+1))

    #Copiando configuracion
    if [ -f /etc/squidban.cfg ]; then
        cp -f squidban.cfg /etc/squidban.cfg.new
        res=$?
        echo -n "[$c] Ya existe /etc/squidban.cfg, lo dejo como esta, pero copio la version limpia en /etc/squidban.cfg.new: "
        [ $res -eq 0 ] && echo "OK" || echo "ERROR"
        c=$(($c+1))

    else
        cp -f squidban.cfg /etc/
        res=$?
        echo -n "[$c] Copiando configuracion, en /etc/squidban.cfg: "
        [ $res -eq 0 ] && echo "OK" || echo "ERROR"
        c=$(($c+1))

    fi

    #Doy los permisos
    chmod 755  -R $RUTA_INSTALACION
    res=$?
    echo -n "[$c] Dando permisos de ejecucion: "
    [ $res -eq 0 ] && echo "OK" || echo "ERROR"
    c=$(($c+1))

    #Copio el script de inicializacion 
    cp -rf init.d/squidban /etc/init.d/
    res=$?
    echo -n "[$c] Copiando script de lanzamiento a /etc/init.d/: "
    [ $res -eq 0 ] && echo "OK" || echo "ERROR"
    c=$(($c+1))

    #Doy los permisos
    chmod 755   /etc/init.d/squidban
    res=$?
    echo -n "[$c] Dando permisos de ejecucion al script de lanzamiento: "
    [ $res -eq 0 ] && echo "OK" || echo "ERROR"
    c=$(($c+1))

    #Genero el enlace
    ln -fs $RUTA_INSTALACION/sc.py /usr/sbin/squidban
    res=$?
    echo -n "[$c] Enlazando sc.py a /usr/sbin/squidcontrol.py: "
    [ $res -eq 0 ] && echo "OK" || echo "ERROR"
    c=$(($c+1))

    echo -e "\n[!] No te olvides de revisar la configuracion antes de lanzarlo"

}

verificar_python(){
    which "python2.7" &>/dev/null
    if [ $? -ne 0 ]; then
        echo "Python2.7 no fue encontrado en el sistema, lo podes instalar haciendo 
        lo siguiente:

           cd /tmp/
           wget http://www.python.org/ftp/python/2.7.3/Python-2.7.3.tgz #Descargo
           tar xvfz Python-2.7.3.tgz #Descomprimo
           cd Python-2.7.3
           ./configure 
           make
           make altinstall #Lo lo instalo sin tocar versiones previas
           ln -fs /usr/local/bin/python2.7 /usr/sbin/python2.7
        "
        exit
    fi

}
    
mostrar_genial_mensaje_de_inicializacion(){
    echo "
      _____         _   _    _____         
     |   __|___ _ _|_|_| |  | __  |___ ___ 
     |__   | . | | | | . |  | __ -| .'|   |
     |_____|_  |___|_|___|  |_____|__,|_|_|
             |_|                           "

    echo -e "\n Observaciones:
        -1 El log propio de este demonio crece, y no es muy util, salvo para hacer Debug
        -2 Procesar por primera vez los logs y los gz consume muchisima RAM, cuidado!
        -3 Para desinstalar descomenta la funcion desinstalar de este script
        "

}

mostrar_genial_mensaje_de_inicializacion

#desinstalar

instalar
