import sys
sys.path.append('/root/cicd_web')
wsgi_app = "cicd.wsgi:application"
loglevel = "debug"
workers = 2
bind = "127.0.0.1:8000"
reload = True
accesslog = errorlog = "/var/log/gunicorn/dev.log"
capture_output = True
pidfile = "/var/run/gunicorn/dev.pid"
daemon = True
