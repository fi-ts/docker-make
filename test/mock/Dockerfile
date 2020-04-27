FROM registry.b.acme/acme/base:7
MAINTAINER foo <foo@bar.com>

 ARG DOCKER_MAKE_VERSION
ENV A=1 \
    B=2 \
    C=3

# A Comment
RUN echo $DOCKER_MAKE_VERSION
CMD ["sdf"]
EXPOSE 80 90
