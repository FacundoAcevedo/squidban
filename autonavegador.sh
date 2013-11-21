#! /bin/bash
#
# autonavegador.sh
# copyleft (>) 2013 Facundo M. Acevedo <facevedo[AT]csjn[DOT]com[DOT]ar>
#
# Distributed under terms of the GPLv3+ license.
#


#Generador magico de navegacion

tiempoFuera=2

rutaAccessLog="/var/log/squid/access.log"

while [ 1 ] ; do
    str="$(date +%s).000 958 5.0.2.20 TCP_MISS/200 2252 CONNECT xmlrpc.rhn.redhat.com:443 - HIER_DIRECT/209.132.183.44 -"
    echo "$str" >> "$rutaAccessLog"
    echo "$str"
    sleep "$tiempoFuera"
done


