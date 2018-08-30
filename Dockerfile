FROM nvidia/cuda:8.0-cudnn5-devel

# install torch deps
RUN apt-get update \
    && apt-get install -y build-essential git gfortran \
    python python-setuptools python-dev \
    cmake curl wget unzip libreadline-dev libjpeg-dev libpng-dev ncurses-dev \
    imagemagick gnuplot gnuplot-x11 libssl-dev libzmq3-dev graphviz htop vim
    

# install openblas
RUN git clone https://github.com/xianyi/OpenBLAS.git /tmp/OpenBLAS \
    && cd /tmp/OpenBLAS \
    && [ $(getconf _NPROCESSORS_ONLN) = 1 ] && export USE_OPENMP=0 || export USE_OPENMP=1 \
    && make -j $(getconf _NPROCESSORS_ONLN) NO_AFFINITY=1 \
    && make install \
    && rm -rf /tmp/OpenBLAS

# install torch
RUN git clone https://github.com/torch/distro.git /torch --recursive \
    && cd /torch \
    && ./clean.sh \
    && TORCH_NVCC_FLAGS="-D__CUDA_NO_HALF_OPERATORS__" ./install.sh \
    && cd ..

# install torch deps
RUN /torch/install/bin/luarocks install rnn \
    && /torch/install/bin/luarocks install dpnn \
    && /torch/install/bin/luarocks install optim \
    && /torch/install/bin/luarocks install cunn \  
    && /torch/install/bin/luarocks install cudnn \ 
    && /torch/install/bin/luarocks install luautf8 \
    && /torch/install/bin/luarocks install penlight \
    && /torch/install/bin/luarocks install moses \
    && /torch/install/bin/luarocks install torchx \
    && /torch/install/bin/luarocks install lua-cjson \
    && /torch/install/bin/luarocks install csv \
    && /torch/install/bin/luarocks install autograd \
    && /torch/install/bin/luarocks install dataload \
    && /torch/install/bin/luarocks install torchnet 


# install cutorch, when we acquire GPUs
RUN git clone https://github.com/torch/cutorch \
    && cd cutorch \
    && mkdir -p $(pwd)/build-nvcc \
    && TORCH_NVCC_FLAGS="--keep --keep-dir=$(pwd)/build-nvcc" /torch/install/bin/luarocks make /cutorch/rocks/cutorch-scm-1.rockspec \
    && rm -rf build-nvcc 

RUN git clone https://github.com/soumith/cudnn.torch.git -b R5 \
    && cd cudnn.torch \
    && mkdir -p $(pwd)/build-nvcc \
    && TORCH_NVCC_FLAGS="--keep --keep-dir=$(pwd)/build-nvcc" /torch/install/bin/luarocks make cudnn-scm-1.rockspec \
    && rm -rf build-nvcc 
#    && /torch/install/bin/luarocks make cudnn-scm-1.rockspec

# set torch env
ENV LUA_PATH='/root/.luarocks/share/lua/5.1/?.lua;/root/.luarocks/share/lua/5.1/?/init.lua;/root/torch/install/share/lua/5.1/?.lua;/root/torch/install/share/lua/5.1/?/init.lua;./?.lua;/root/torch/install/share/luajit-2.1.0-alpha/?.lua;/usr/local/share/lua/5.1/?.lua;/usr/local/share/lua/5.1/?/init.lua' \
    LUA_CPATH='/root/.luarocks/lib/lua/5.1/?.so;/root/torch/install/lib/lua/5.1/?.so;./?.so;/usr/local/lib/lua/5.1/?.so;/usr/local/lib/lua/5.1/loadall.so' \
    PATH=/root/torch/install/bin:$PATH \
    LD_LIBRARY_PATH=/root/torch/install/lib:$LD_LIBRARY_PATH \
    DYLD_LIBRARY_PATH=/root/torch/install/lib:$DYLD_LIBRARY_PATH

# clean up
RUN apt-get autoremove && apt-get clean && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*
