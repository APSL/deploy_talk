import sys
sys.path.insert(0, './djangoapp')
from djangoapp import wsgi


app = wsgi.application
