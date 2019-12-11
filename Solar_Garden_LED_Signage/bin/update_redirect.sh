#!/bin/bash

# author: Tyler Thompson
# created: Oct 31, 2019
# description: Intended to run in the Solar Garden LED Signage and send its ip address back to the data collection server.
# The data collection server uses apache to redirect requests to the LED sign.

SERVER_IP="141.218.140.193" # the ip address of the apache server
SERVER_CONFIG="/etc/apache2/sites-available/led_sign.conf" # the config file locatioin on the apache server
IFACE_NAME="wlan0" # the local network interface to query for an ip address
IP_FILE="/tmp/current_ip.txt" # a temporary file to read and write the ip address to

IP_ADDR=$(/sbin/ifconfig ${IFACE_NAME} | grep -Eo 'inet (addr:)?([0-9]*\.){3}[0-9]*' | grep -Eo '([0-9]*\.){3}[0-9]*')
APACHE_CONFIG="<VirtualHost *:80>\nServerName $SERVER_IP\nRedirect / http://$IP_ADDR\n</VirtualHost>"
#IPTABLES_RULE="/sbin/iptables -t nat -D PREROUTING 1; /sbin/iptables -t nat -A PREROUTING -p tcp -d $SERVER_IP --dport 80 -j DNAT --to-destination $IP_ADDR:80;"

update_server() {
  ssh root@$SERVER_IP -o StrictHostKeyChecking=no -o BatchMode=yes -o ConnectTimeout=5 -C "printf '$APACHE_CONFIG' > '$SERVER_CONFIG'; service apache2 restart"
#  ssh root@$SERVER_IP -o StrictHostKeyChecking=no -o BatchMode=yes -o ConnectTimeout=5 -C "$IPTABLES_RULE"
  echo "${IP_ADDR}" > "${IP_FILE}"
}

main() {
  if [[ ! -f  "${IP_FILE}" || "$1" == "-f" ]]; then
    echo "Current ip address file not found. Creating it and updating the server with current ip address $IP_ADDR"
    update_server
  else
    if [[ "$(cat ${IP_FILE})" != "${IP_ADDR}" ]]; then
      echo "Ip address change detected. Updating the server with current ip address $IP_ADDR"
      update_server
    else
      echo "No ip address change has been detected."
    fi
  fi
}

main "$@"
exit 0
