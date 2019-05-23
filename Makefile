include make.mk

.PHONY: init run

init:
	pip3 install -r requirements.txt

run:
	FLASK_APP=aufwerter.py flask run

deploy:
	tar czf aufwerter.tar.gz aufwerter.py wsgi.py requirements.txt setup.py templates/* env aufwerter.service
	ssh ${REMOTE_USER}@${REMOTE_HOST} "rm -rf /home/${REMOTE_USER}/aufwerter && mkdir -p /home/${REMOTE_USER}/aufwerter && mkdir -p /home/${REMOTE_USER}/.config/systemd/user"
	scp aufwerter.tar.gz ${REMOTE_USER}@${REMOTE_HOST}:/home/${REMOTE_USER}/aufwerter
	ssh ${REMOTE_USER}@${REMOTE_HOST} "cd /home/${REMOTE_USER}/aufwerter && tar xzf aufwerter.tar.gz &&  rm aufwerter.tar.gz && cp -f /home/${REMOTE_USER}/aufwerter/aufwerter.service /home/${REMOTE_USER}/.config/systemd/user/ && systemctl --user daemon-reload && sleep 3 && systemctl --user restart aufwerter.service"
	rm aufwerter.tar.gz
