#!/bin/bash

NUM=1
NUM_MAX=16
TIMEOUT=180
ORG_PATH=/var/www/html/sqs-batch-server
_PYTHON_PATH=/home/ubuntu/myproject/myprojectenv/bin/python
_GUNICORN_PATH=/home/ubuntu/myproject/myprojectenv/bin/gunicorn

for i in $(seq 1 ${NUM_MAX}); do systemctl disable $i.keras.service; done

for i in $(seq 1 ${NUM}); do \
cat << EOF > /etc/systemd/system/$i.keras.service

[Unit]
Description = Keras middleware No.$i
After=network.target

[Service]
Restart = always
WorkingDirectory=${ORG_PATH}
ExecStart = ${_PYTHON_PATH} ${_GUNICORN_PATH} --timeout ${TIMEOUT} --log-file /var/log/keras.log --workers 1 --bind 127.0.0.1:500$i wsgi:app
ExecReload = /bin/kill -s HUP \${MAINPID}
KillSignal = QUIT

[Install]
WantedBy = multi-user.target
EOF
done

for i in $(seq 1 ${NUM}); do systemctl daemon-reload; systemctl restart $i.keras.service; done
for i in $(seq 1 ${NUM}); do systemctl enable $i.keras.service; done
for i in $(seq 1 ${NUM}); do echo "            server 127.0.0.1:500$i;"; done > txt


cat << EOF > /etc/nginx/nginx.conf
user www-data;
worker_processes auto;
pid /run/nginx.pid;
events {
	worker_connections 768;
}
http {
	sendfile on;
	tcp_nopush on;
	tcp_nodelay on;
        keepalive_timeout  ${TIMEOUT};
        send_timeout ${TIMEOUT};
        client_body_timeout ${TIMEOUT};
        client_header_timeout ${TIMEOUT};
        proxy_send_timeout ${TIMEOUT};
        proxy_read_timeout ${TIMEOUT};
	types_hash_max_size 2048;
	include /etc/nginx/mime.types;
	default_type application/octet-stream;
	ssl_protocols TLSv1 TLSv1.1 TLSv1.2;
	ssl_prefer_server_ciphers on;
	access_log /var/log/nginx/access.log;
	error_log /var/log/nginx/error.log;
	gzip on;
	gzip_disable "msie6";

        upstream app {
$(cat txt)
        }
        server {
            root ${ORG_PATH};
            include proxy_params;
            location / {
                proxy_pass http://app;
            }
        }
}
EOF

systemctl restart nginx.service

rm txt

