#!/bin/sh

case "$1" in
start)
	printf "Starting camera streaming.."
	start-stop-daemon --background --chuid user --start --exec /home/user/n800stream.sh
	printf ".\n"
	;;

stop)
	start-stop-daemon --stop --exec /bin/sh /home/user/n800stream.sh
	;;

*)
	printf "Usage: /etc/init.d/n800streaminit.sh {start|stop}\n" >&2
	exit 1
	;;
esac


exit 0
