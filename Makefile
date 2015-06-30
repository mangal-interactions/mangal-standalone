.PHONY: clean

ALL: mangal

mangal: exec
	./manage.py syncdb

requirements:
	pip install django==1.7
	pip install django-tastypie

clean:
	# Remove pyc files
	find . -name "*.pyc" | xargs rm

exec:
	chmod +x manage.py
