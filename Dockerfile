FROM python:alpine3.6
ARG VERSION=v0.6.6

ENV PYTHONUNBUFFERED 1

RUN apk add --no-cache shadow
RUN useradd --user-group --create-home --home-dir /flask --shell /bin/false flask

RUN apk add --no-cache linux-headers make gcc musl-dev libxml2-dev libxslt-dev libffi-dev postgresql-dev git

RUN pip install --upgrade pip && pip install --no-cache-dir -e git+https://github.com/briancappello/flask-unchained.git@${VERSION}#egg=flask-unchained

WORKDIR /flask/src

USER flask

CMD ["flask", "run", "--host", "0.0.0.0", "--port", "5000"]
EXPOSE 5000