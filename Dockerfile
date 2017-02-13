FROM python:3.6-alpine
RUN apk update
RUN apk add bash
WORKDIR /srv
COPY run.py /srv/run.py
RUN mkdir -p /srv/wheels
COPY dist/*.whl /srv/wheels
RUN bash -c "pip install /srv/wheels/*"
CMD python /srv/run.py
EXPOSE 5000