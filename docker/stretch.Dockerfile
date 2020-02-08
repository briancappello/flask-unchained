FROM python:3.6-stretch
ARG VERSION=v0.7.0

ENV PYTHONUNBUFFERED 1

RUN useradd --user-group --create-home --home-dir /flask --shell /bin/false flask

RUN apt-get update && apt-get install -y build-essential libxml2-dev libxslt-dev libffi-dev libpq-dev git

RUN pip install --upgrade pip && pip install --no-cache-dir -e git+https://github.com/briancappello/flask-unchained.git@${VERSION}#egg=flask-unchained

WORKDIR /flask/src

USER flask

CMD ["flask", "run", "--host", "0.0.0.0", "--port", "5000"]
EXPOSE 5000
