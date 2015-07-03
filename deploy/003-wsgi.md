# Servidores de aplicaciones python


<img src='img/lsbaws_part2_before_wsgi.png' />

http://ruslanspivak.com/lsbaws-part2/

---

# Ejemplo: Apache + mod_python + Django

    !xml
    # from the past!
    <Location "/mysite/">
        SetHandler python-program
        PythonHandler django.core.handlers.modpython
        SetEnv DJANGO_SETTINGS_MODULE mysite.settings
        PythonOption django.root /mysite
        PythonDebug On
    </Location>

---

# Servidores de aplicaciones python

<img src='img/lsbaws_part2_after_wsgi.png' />


---

# Python Web Server Gateway Interface

<img src='img/lsbaws_part2_wsgi_idea.png' />

https://www.python.org/dev/peps/pep-0333/


---

# Web Server Gateway Interface

<img src='img/lsbaws_part2_wsgi_interop.png' />

---

# WSGI

<img src='img/lsbaws_part2_wsgi_interface.png' />

---

# Ejemplo WSGI: simple callable

    !python
    # simple.py
    def app(environ, start_response):
        status = '200 OK' # HTTP Status
        headers = [('Content-type', 'text/plain')] # HTTP Headers
        start_response(status, headers)
        return ["Hello from ", "simple app", ]

---

# Ejemplo WSGI: aplicación Flask

    !python
    # flaskapp.py
    from flask import Flask
    from flask import Response
    flask_app = Flask('flaskapp')


    @flask_app.route('/hello')
    def hello_world():
        return Response(
            'Hello world from Flask!\n',
            mimetype='text/plain'
        )

    app = flask_app.wsgi_app

---

# Ejemplo WSGI: aplicación django

    !python
    # djangoapp/views.py
    from django.http import HttpResponse
    def index(request):
        return HttpResponse(
            'Hello world from Django!\n',
            content_type='text/plain'
        )

    # djangoapp/urls.py
    from django.conf.urls import patterns, include, url
    from django.contrib import admin
    urlpatterns = patterns('',
        url(r'^hello/', 'djangoapp.views.index'),
        url(r'^admin/', include(admin.site.urls)),
    )

    # djangoapp/wsgi.py
    import os
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")
    from django.core.wsgi import get_wsgi_application
    application = get_wsgi_application()

---

# Servidor de aplicaciones python en producción

* Tareas a gestionar:
    * Abrir socket y compartirlo
    * Crear procesos prefork (+ threads)
    * Supervisar procesos
    * Escalar procesos ?
    * Inicializar Virtualenv
    * ¿Dónde guardamos la configuración?

* Nuestro app server tendrá varios componentes que se repartirán la responsabilidad de cada tarea.

---

# gunicorn

* http://gunicorn.org/
* python WSGI server
* Modelo servidor: 
    * Síncrono: prefork
    * Asíncrono 
        * greenlets
        * tornado
        * asyncio
* pip install gunicorn

gunicorn -w 2 flaskapp:app
gunicorn -w 2 djangoapp.wsgi:application

---

# chaussette 

* http://chaussette.readthedocs.org/
* python WSGI server
* Múltiples backends:
    * gevent – based on Gevent’s pywsgi server
    * fastgevent – based on Gevent’s wsgi server – faster but does not support streaming.
    * meinheld – based on Meinheld’s fast C server
    * waitress – based on Pyramid’s waitress pure Python web server (py3)
    * eventlet – based on Eventlet’s wsgi server
    * geventwebsocket – Gevent’s pywsgi server coupled with geventwebsocket handler.
    * geventws4py – Gevent’s pywsgi server coupled with ws4py handler.
    * socketio – based on gevent-socketio, which is a custom Gevent server & handler that manages the socketio protocol.
    * bjoern – based on Bjoern.
    * tornado – based on Tornado’s wsgi server.
* Pensado para no gestionar el socket

---

# uwsgi

* Servidor WSGI implementado en C
* Alto rendimiento
* modo prefork, soporta combinación de procesos y threads
* Reinicio graceful
* Protocolo uwsgi comunicación con web server (también server propio)

. 

    !bash
    uwsgi --http :8000 --module flaskapp:app   \
     --master --processes 4  --threads 2

---

# Servidor de aplicaciones python en producción

* Tareas a gestionar:
    * Abrir socket:  
        * uwsgi, gunicorn, circusd
    * Prefork procesos:
        * uwsgi, gunicorn, circusd
    * Supervisar procesos:
        * supervisord, circusd, upstart, systemd, uwsgi
    * Activar Virtualenv:
        * circusd, uwsgi, bash
    * Servidor wsgi:
        * chaussette, uwsgi, gunicorn
    * Servir estáticos
        * nginx, uwsgi, gunicorn

---

# Servidor de aplicaciones python: combinaciones

* supervisord + uwsgi
* supervisord + gunicorn
* circusd + chaussette
* circusd + uwsgi

---

# Servidor de aplicaciones python: supervisor

¿Por qué no usamos sysvinit, upstart, systemd? 

* Monitorización del proceso: fork() vs "vigilar" el PID
    * No queremos ni oir hablar de *start-stop-daemon* :P
* Gestión redirección de stdout y stderr (logs)
* Parámetros app-friendly (chdir, virtualenv.. )
* formato .ini
* En el caso de circusd, muchas tareas extra (sockets, virtualenv, escalado, stats...)

---

# Gestionar el virtualenv para desplegar

## Usuario dedicado

    !bash
    groupadd -g 500 creantbits
    useradd -g 500 -d /creantbits -m -s /bin/bash creantbits

## pip install virtualenvwrapper


    !bash
    export WORKON_HOME=$HOME/.virtualenvs
    source /usr/local/bin/virtualenvwrapper.sh
    
    mkvirtualenv django
    workon django


## pip install pew

    !bash
    export WORKON_HOME=$HOME/.virtualenvs
    PS1="\[\033[01;34m\]\$(basename '$VIRTUAL_ENV')\e[0m$PS1"

    pew-new django
    pew-workon django
    pew-in django python manage.py runserver
    

---

# circus

http://circus.readthedocs.org/en/latest/

    !bash
    pip install circus
    pip install circus-web

---

# circusd appserver

    !ini
    [circus]
    httpd = True
    statsd = True
    httpd_host = 0.0.0.0
    httpd_port = 8080

    [watcher:creantbits]
    working_dir = /creantbits/djangoapp
    cmd = /usr/local/bin/chaussette --fd $(circus.sockets.creantbits) djangoapp.wsgi.application
    #working_dir = /creantbits
    #cmd = /usr/local/bin/chaussette --fd $(circus.sockets.creantbits) flaskapp.app
    numprocesses = 60
    use_sockets = True
    uid = django
    gid = django
    virtualenv = /var/pywww/creantbits/.virtualenvs/creantbits
    copy_env = True

    [socket:creantbits]
    host = 0.0.0.0
    port = 8000


---

# uwsgi.ini

    !ini
    [uwsgi]
    socket = /tmp/creantbits.sock
    http = :8000
    chmod-socket = 666
    master = true
    processes = 4
    threads = 5
    harakiri = 60
    max-requests = 2000
    chdir = /creantbits/djangoapp
    pythonpath = /creantbits/djangoapp
    virtualenv = /creantbits/.virtualenvs/creantbits
    #env = DJANGO_SETTINGS_MODULE=djangoapp.settings
    #module = django.core.handlers.wsgi:WSGIHandler()
    module = djangoapp.wsgi
    uid = creantbits
    gid = creantbits
    vacuum = true
    touch-reload = /tmp/creantbits.reload
    #static-map = /static=/tmp/static
    #static-map = /media=/tmp/media
    disable-logging = 0
    memory-report = 1
    log-master = 1
    log-date = 1
    log-slow = 1
    log-4xx = 1
    log-sendfile = 1
    log-micros = 0
    log-slow = 1

---

# supervisor

    !ini
    [program:trespamsz]
    command = /usr/local/bin/uwsgi --ini /etc/uwsgi-prod.d/trespamsz.ini
    directory = /tmp
    user=trespamsz
    process_name=trespamsz
    numprocs=1
    autostart=true
    redirect_stderr=true
    stdout_logfile=/var/log/apps-prod/trespamsz-uwsgi.log
    priority=10
    umask=002
    stopsignal=QUIT


---

# nginx

    !bash
    # uwsgi
    location / {
        include uwsgi_params;
        uwsgi_pass 127.0.0.1:3031;
    }
    # proxy
    location / {
        include proxy_params;
        proxy_pass http://localhost:8000;
    }


---

# ejemplo nginx

    !bash
    server {
        listen 80;
        server_name trespams.com;
        access_log  /var/log/nginx/trespamsz-access.log;
        error_log  /var/log/nginx/trespamsz-error.log;

        location / {
            uwsgi_pass unix:/var/pywww/trespamsz/nginx.sock;
            include uwsgi_params;
        }

        location /media/trespamsz {
            root /var/www;
            expires max;
            access_log off;
        }
        location /static/trespamsz {
            root /var/www;
            expires max;
            access_log off;
        }
        location ~ /\.hg {
            deny  all;
        }
    }


--- 

# Consideraciones nginx en producción

## timeouts 

    !bash
    client_body_timeout 12;
    client_header_timeout 12;
    send_timeout 10;
    keepalive_timeout 15;

* nginx
* uwsgi_params
* uwsgi.ini (harakiri)

---

# GRACIAS!

* http://talks.apsl.net/deploy_python/
* https://github.com/APSL/deploy_talk

* Thanks to:
    * https://gallir.wordpress.com/principios-de-concurrencia/
    * http://ruslanspivak.com/lsbaws-part1/
    * http://ruslanspivak.com/lsbaws-part2/
    * http://berb.github.io/diploma-thesis/community/index.html
    * landslide python: https://github.com/adamzap/landslide                       
    * avalanche lanslide theme:  https://github.com/akrabat/avalanche       
