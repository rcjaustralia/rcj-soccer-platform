#!/usr/bin/env bash
sudo easy_install pip
sudo pip install virtualenv
mkdir -p /var/apps/$1/env/
virtualenv /var/apps/$1/env/

source /var/apps/$1/env/bin/activate
pip install -r requirements.txt
sudo pip install uwsgi

echo "[Unit]
Description=uWSGI instance to serve $1
After=network.target

[Service]
User=root
Group=nginx
WorkingDirectory=/var/apps/$1/
Environment='PATH=/var/apps/$1/env/bin'
ExecStart=/usr/bin/bash -c 'source /var/apps/$1/env/bin/activate; cd /var/apps/$1/; /var/apps/$1/env/bin/uwsgi --ini /var/apps/$1/conf/wsgi.ini'

[Install]
WantedBy=multi-user.target" > /etc/systemd/system/$1.service

mkdir -p conf
echo "[uwsgi]
module = wsgi

master = true
processes = 10

socket = /var/apps/$1/conf/app.sock
chmod-socket = 660
vacuum = true
virtualenv = /var/apps/$1/env/
manage-script-name = true
die-on-term = true" > /var/apps/$1/conf/wsgi.ini

sudo systemctl enable $1

echo "Add the following to /etc/nginx/nginx.conf, then restart nginx:"
echo "    server {
        listen       80;
        listen       [::]:80;
        server_name  $1.robocup.tech;
        root         /usr/share/nginx/html;

        # Load configuration files for the default server block.
        include /etc/nginx/default.d/*.conf;

        location / {
			include uwsgi_params;
			uwsgi_pass unix:/var/apps/$1/conf/app.sock;
        }

        error_page 404 /404.html;
            location = /40x.html {
        }

        error_page 500 502 503 504 /50x.html;
            location = /50x.html {
        }
    }"
sudo systemctl start $1
sudo systemctl status $1