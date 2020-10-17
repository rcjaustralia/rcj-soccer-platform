FROM centos:7

RUN yum upgrade -y && \
    yum install -y https://repo.ius.io/ius-release-el7.rpm && \
    yum install -y python36u python36u-devel python36u-pip mariadb

EXPOSE 5000

WORKDIR /srv

COPY run.py /srv/run.py
COPY run.sh /srv/run.sh

RUN mkdir -p /srv/wheels

COPY dist/*.whl /srv/wheels

RUN pip3.6 install /srv/wheels/*

CMD [ "bash", "run.sh" ]
