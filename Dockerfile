FROM centos:7

MAINTAINER Tristan Roberts <tristan_roberts@icloud.com>

EXPOSE 80

RUN yum upgrade -y && \
    yum install -y python-devel nginx && \
    mkdir -p /app/

WORKDIR /app/

COPY . /app/

RUN pip install -r /app/requirements.txt

CMD [ "python", "/app/wsgi.py" ]