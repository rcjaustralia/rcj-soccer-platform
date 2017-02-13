FROM centos:7

MAINTAINER Tristan Roberts <tristan_roberts@icloud.com>

EXPOSE 80

RUN yum install -y epel-release && \
    yum upgrade -y && \
    yum install -y python-devel python2-pip && \
    yum remove -y epel-release && \
    mkdir -p /app/ && \
    pip install --upgrade pip

WORKDIR /app/

COPY . /app/

RUN pip install -r /app/requirements.txt

CMD [ "python", "/app/wsgi.py" ]
