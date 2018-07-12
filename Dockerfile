FROM python:3.6.5-alpine

RUN apk update && apk add git build-base python3-dev libxslt-dev

WORKDIR /api
RUN pip install git+https://github.com/openprocurement/ocdsapi.git

ADD requirements.txt .
RUN pip install -r requirements.txt

ADD . .
RUN pip install .
ENTRYPOINT ["ocds-server"]
CMD ["--config", "server.yml"]
