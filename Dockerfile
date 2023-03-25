# latch base image + dependencies for latch SDK --- removing these will break the workflow
FROM 812206152185.dkr.ecr.us-west-2.amazonaws.com/latch-base:9c8f-main
RUN pip install latch==2.14.2
RUN mkdir /opt/latch

RUN apt-get install -y curl unzip libz-dev

# Kaiju installation
RUN curl -L \
    https://github.com/bioinformatics-centre/kaiju/releases/download/v1.9.0/kaiju-v1.9.0-linux-x86_64.tar.gz -o kaiju-v1.9.0.tar.gz &&\
    tar -xvf kaiju-v1.9.0.tar.gz

ENV PATH /root/kaiju-v1.9.0-linux-x86_64-static:$PATH

# Krona installation
RUN curl -L \
    https://github.com/marbl/Krona/releases/download/v2.8.1/KronaTools-2.8.1.tar \
    -o KronaTools-2.8.1.tar &&\
    tar -xvf KronaTools-2.8.1.tar &&\
    cd KronaTools-2.8.1 &&\
    ./install.pl

# copy all code from package (use .dockerignore to skip files)
COPY . /root/

# latch internal tagging system + expected root directory --- changing these lines will break the workflow
ARG tag
ENV FLYTE_INTERNAL_IMAGE $tag
WORKDIR /root