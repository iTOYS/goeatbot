FROM python:3

COPY requirements.txt /home/docker/code
RUN pip install --no-cache-dir -r /home/docker/code/requirements.txt
COPY . /home/docker/code/

RUN cd /home/docker/code/app/ && python3 bot.py

EXPOSE 5555