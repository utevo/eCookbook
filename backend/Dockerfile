FROM python:3.8-alpine

ENV PYTHONUNBUFFERED 1

WORKDIR /app

COPY requirements.txt requirements.txt
RUN apk add --update --no-cache postgresql-client jpeg-dev
RUN apk add --update --no-cache --virtual .tmp-build-deps \
        gcc libc-dev linux-headers postgresql-dev zlib zlib-dev musl-dev
RUN pip install -r requirements.txt
RUN apk del .tmp-build-deps

RUN mkdir -p /vol/web/media
RUN mkdir -p /vol/web/static

RUN adduser -D user
RUN chown -R user:user /vol/
RUN chmod -R 755 /vol/ 
USER user

ENV PATH $PATH:~/.local/bin