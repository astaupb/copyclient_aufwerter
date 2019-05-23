# to run:

1. create environ.sh accordingly to environ.sh.template

2. run
```
source environ.sh
make run
```

# creating a systemd service quickly:

1. add environment variables to ~/.env and install requirements

2. create user service like this

```
[Unit]
AssertPathExists=/usr/bin/gunicorn
After=network-online.target
Wants=network-online.target

[Service]
WorkingDirectory=/home/user/aufwerter/
EnvironmentFile=/home/user/.env
ExecStart=/usr/bin/gunicorn --bind 127.0.0.1:8002 wsgi
Restart=always
PrivateTmp=true
NoNewPrivileges=true

[Install]
WantedBy=default.target
```