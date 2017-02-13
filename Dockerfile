FROM centos:7

MAINTAINER Tristan Roberts <tristan_roberts@icloud.com>

EXPOSE 80

RUN yum install -y epel-release && \
    yum upgrade -y && \
    yum install -y python-devel python2-pip mysql gcc libev-devel libev && \
    yum remove -y epel-release && \
    mkdir -p /app/ && \
    pip install --upgrade pip

WORKDIR /app/

COPY requirements.txt /app/requirements.txt

RUN pip install -r /app/requirements.txt

COPY . /app/

RUN chmod +x /app/run.sh

CMD [ "bash", "/app/run.sh" ]
