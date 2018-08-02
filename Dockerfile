ARG base_image
FROM ${base_image}

# install ixmp
RUN git clone https://github.com/iiasa/ixmp.git /ixmp
RUN cd /ixmp && python setup.py install

# install message_ix
COPY . /message_ix
WORKDIR /
RUN cd /message_ix && python setup.py install 
