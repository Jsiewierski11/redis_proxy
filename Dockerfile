FROM ubuntu:focal
RUN echo 'debconf debconf/frontend select Noninteractive' | debconf-set-selections

RUN apt-get update \
  && apt-get install -y -q --no-install-recommends \
    python3-dev \
    python3-pip \
  && cd /usr/local/bin \
  && ln -s /usr/bin/python3 python \
  && pip3 install --upgrade pip

WORKDIR /usr/src/app

ENV PYTHONPATH="/usr/src/app/src:/usr/src/app/src/proxy"
ENV CONFIGS="./configs/config.yml"
COPY requirements.txt /usr/src/app
RUN pip install -r requirements.txt

EXPOSE 5000