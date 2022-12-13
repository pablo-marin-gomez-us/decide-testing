import os

ALLOWED_HOSTS = ["*"]

# Modules in use, commented modules that you won't use
MODULES = [
    'authentication',
    'base',
    'booth',
    'census',
    'mixnet',
    'postproc',
    'store',
    'visualizer',
    'voting',
]
BASEURL = os.environ.get('baseurl')

APIS = {
    'authentication': BASEURL,
    'base': BASEURL,
    'booth': BASEURL,
    'census': BASEURL,
    'mixnet': BASEURL,
    'postproc': BASEURL,
    'store': BASEURL,
    'visualizer': BASEURL,
    'voting': BASEURL,
}



DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'decide_mnde_azm2',
        'USER': 'decide',
        'HOST': os.environ.get('host'),
        'PORT': '5432',
        'PASSWORD':os.environ.get('password')
    }
}



# number of bits for the key, all auths should use the same number of bits
KEYBITS = 256
