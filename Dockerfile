FROM gidden/messageix-base

RUN git clone git@github.com:iiasa/ixmp /ixmp && cd /ixmp && python setup.py install

COPY . /message_ix
WORKDIR /
RUN cd /message_ix && python2 setup.py install 
RUN cd /message_ix && python3 setup.py install
