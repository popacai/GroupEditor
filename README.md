GroupEditor
===========

Group based co-editor. By using [A/C/G]BCAST

===========

python final_test.py [local_ip_addr] [local port] [remote ip addr] [remote port]

start a new group: 
python final_test.py [local_ip_addr] [local port] n 1

==========

To start 4 users
python final_test.py 127.0.0.1 10000 n 1
python final_test.py 127.0.0.1 10001 127.0.0.1 10000
python final_test.py 127.0.0.1 10002 127.0.0.1 10001
python final_test.py 127.0.0.1 10003 127.0.0.1 10002

Use Ctrl ^ C to exit. Please don't use the :q to quit. 

