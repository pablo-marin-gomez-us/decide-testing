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
BASEURL = 'https://decide-qvzx.onrender.com'

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
        'HOST': 'dpg-ceaahp2rrk0bbtbpfdqg-a.frankfurt-postgres.render.com',
        'PORT': '5432',
        'PASSWORD':'2wKeyTjR1yVNmHfB8daRTMVISv9iNlnu'
    }
}



# number of bits for the key, all auths should use the same number of bits
KEYBITS = 256
