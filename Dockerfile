FROM python:3.11.8-alpine

ENV PYTHONUNBUFFERED 1

RUN pip install --upgrade pip

RUN apk update \
  # psycopg2 dependencies
  && apk add --virtual .build-deps \
  gcc \
  python3-dev \
  musl-dev \
  openssl-dev\
  cargo \
  postgresql-dev \
  libffi-dev\
  py-cffi \
  build-base\
  && apk add jpeg-dev zlib-dev freetype-dev lcms2-dev openjpeg-dev tiff-dev tk-dev tcl-dev \
  # Translations dependencies
  && apk add gettext \
  # https://docs.djangoproject.com/en/dev/ref/django-admin/#dbshell
  && apk add postgresql-client \
  && apk add make \
  # git
  && apk add git \
  && apk add curl

COPY requirements.txt requirements.txt

RUN pip install -r requirements.txt && apk del .build-deps

RUN mkdir /app/
WORKDIR /app
COPY . .

ENTRYPOINT [ "sh", "entrypoint.sh" ]