# cabinet
A very simple web app for organizing information tidbits

This app is a single-user tool that I'm making to better understand web development (and also to organize my infodump in a navigable and intuitive way).

It utilizes postgres 9.6 and python/flask for backend and pure html/js for frontend (so far).

Installation order:
1) Install Python 3.7.2
2) Create venv folder within project folder: py -3 -m venv venv
3) Activate venv
4) Upgrade pip and install modules:
	python -m pip install --upgrade pip
	pip install Flask
	pip install flask-talisman
	pip install pyopenssl
	pip install psycopg2
5) (For localhost https testing) create self-signed cert and key and place them in the /cabinet/security folder:
	from werkzeug.serving import make_ssl_devcert
	make_ssl_devcert('/path/to/the/key', host='localhost')