FROM ubuntu:18.04

LABEL maintainer="brainbow@my.bcit.ca"

RUN apt-get update -y && \
    apt-get install -y python3 python3-pip
    
COPY . /app

WORKDIR /app

RUN pip3 install --upgrade pip && pip3 install -r requirements.txt

ENTRYPOINT [ "python3" ]

CMD [ "app.py" ]