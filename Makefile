.PHONY: clean

ALL: mangal exec

mangal: mangal_ref
	cp mangal_ref mangal

requirements:
	pip install django==1.7
	pip install django-tastypie

clean:
	find . -name "*.pyc" | xargs rm

exec:
	chmod +x manage.py

reset:
	git fetch --all
	git reset --hard origin/master
