.PHONY: init run

init:
	pip3 install -r requirements.txt

run:
	FLASK_APP=aufwerter.py flask run
