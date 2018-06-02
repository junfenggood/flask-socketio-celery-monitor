FROM python:2.7
RUN mkdir /monitor
WORKDIR /monitor
COPY . /monitor/
RUN pip install -r requirements.txt
CMD ["supervisord", "-c", "supervisor.conf"]