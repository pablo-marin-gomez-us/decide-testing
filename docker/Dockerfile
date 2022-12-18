from nickgryg/alpine-pandas:3.7

RUN apk add --no-cache git postgresql-dev gcc libc-dev
RUN apk add --no-cache gcc g++ make libffi-dev python3-dev build-base gettext

RUN pip install gunicorn
RUN pip install psycopg2
RUN pip install ipdb
RUN pip install ipython

WORKDIR /app

RUN git clone https://github.com/Villanueva-del-Trabuco-EGC/decide.git .
RUN pip install -r requirements.txt

WORKDIR /app/docker

# local settings.py
ADD docker-settings.py /app/decide/local_settings.py
ADD entorno.env /app/decide/.env

WORKDIR /app/decide


RUN django-admin makemessages
RUN django-admin compilemessages


#CMD ["gunicorn", "-w 5", "decide.wsgi", "--timeout=500", "-b 0.0.0.0:5000"]