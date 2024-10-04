FROM python:3.12.7-bookworm
LABEL maintainer="Tamas Gal <tgal@km3net.de>"

 ENV INSTALL_DIR /km3io

 RUN apt-get update
 RUN apt-get install -y -qq git python3-pip && apt-get -y clean && apt-get autoclean
 RUN python3 -m pip install --upgrade pip setuptools wheel

 ADD . $INSTALL_DIR
 RUN cd $INSTALL_DIR && python3 -m pip install . ".[dev]" ".[extras]"

 # Clean up
 RUN cd / && rm -rf $INSTALL_DIR
 RUN rm -rf /var/cache
