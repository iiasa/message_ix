FROM gidden/messageix-base

COPY . /message_ix
WORKDIR /
RUN cd /message_ix && python2 setup.py install 
RUN cd /message_ix && python3 setup.py install
