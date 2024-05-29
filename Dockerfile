FROM python:3.11.8-alpine as base

FROM base as builder

RUN mkdir /install
WORKDIR /install

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
  build-base

COPY requirements.txt requirements.txt

RUN pip install --prefix=/install -r requirements.txt \
  && apk del .build-deps \
  && rm requirements.txt

FROM base

COPY --from=builder /install /usr/local

ENV PYTHONUNBUFFERED 1

RUN apk update \
  && apk add postgresql-client \
  && apk add curl

RUN mkdir /app/
WORKDIR /app
COPY . .

ENTRYPOINT [ "sh", "entrypoint.sh" ]