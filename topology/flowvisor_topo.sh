#config the flowvisor 
sudo -u mininet fvconfig generate /etc/flowvisor/config.json


#start the flowvisor
sudo /ect/init.d/flowvisor start






fvctl -f /dev/null add-slice large  tcp:localhost:10001 admin@slice
fvctl -f /dev/null add-slice small  tcp:localhost:10002 admin@slice

dpctl add-queue tcp:localhost 1 1 4
dpctl add-queue tcp:localhost 1 2 1


