ARG base_image
FROM ${base_image}

RUN conda install --yes pyyaml
RUN conda install --yes -c conda-forge ixmp pyam

# install ixmp
RUN git clone https://github.com/iiasa/ixmp.git /ixmp
RUN cd /ixmp && python setup.py install
RUN cd ..

# install pyam
RUN git clone https://github.com/IAMconsortium/pyam.git /pyam
RUN cd /pyam && python setup.py install

# install message_ix
COPY . /message_ix
WORKDIR /
RUN cd /message_ix && python setup.py install 
