FROM gidden/messageix-base

COPY . /message_ix
WORKDIR /
ENV IXMP_PATH /message_ix
ENV IXMP_R_PATH /message_ix/ixmp
RUN cd /message_ix/ixmp && python2 setup.py install 
RUN cd /message_ix && python2 setup.py install 
RUN cd /message_ix/ixmp && python3 setup.py install
RUN cd /message_ix && python3 setup.py install
