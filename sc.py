#!/usr/bin/env python2.7
import sys
from squidcontrol import SquidControl

if __name__ == "__main__":
    daemon = SquidControl('/tmp/squid_control.pid',
             stdout="/dev/stdout", stderr="/dev/stderr")

    if len(sys.argv) == 2:
        if 'start' == sys.argv[1]:
            daemon.start()
        if 'runalone' == sys.argv[1]:
            daemon.runalone()
        elif 'stop' == sys.argv[1]:
            daemon.stop()
        elif 'restart' == sys.argv[1]:
            daemon.restart()
        else:
            print "Comando desconocido"
            sys.exit(2)
        sys.exit(0)
    else:
        print "Uso: %s start|runalone|stop|restart" % sys.argv[0]
    sys.exit(2)
