FROM gidden/messageix-base

RUN git clone https://github.com/iiasa/ixmp.git /ixmp
RUN cd /ixmp && python2 setup.py install
RUN cd /ixmp && python3 setup.py install

COPY . /message_ix
WORKDIR /
RUN cd /message_ix && python2 setup.py install 
RUN cd /message_ix && python3 setup.py install
