# latch base image + dependencies for latch SDK --- removing these will break the workflow
FROM 812206152185.dkr.ecr.us-west-2.amazonaws.com/latch-base:9c8f-main
RUN pip install latch==2.14.2
RUN mkdir /opt/latch

# latch internal tagging system + expected root directory --- changing these lines will break the workflow
ARG tag
ENV FLYTE_INTERNAL_IMAGE $tag
WORKDIR /root