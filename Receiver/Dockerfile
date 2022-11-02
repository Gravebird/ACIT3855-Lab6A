FROM ubuntu:18.04

LABEL maintainer="brainbow@my.bcit.ca"

RUN apt-get update -y && \
    apt-get install -y python3 curl
    
RUN curl https://bootstrap.pypa.io/pip/3.6/get-pip.py | python3
    
COPY . /app

WORKDIR /app

RUN pip install 

RUN pip install -r requirements.txt

ENTRYPOINT [ "python3" ]

CMD [ "app.py" ]