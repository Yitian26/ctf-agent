FROM ubuntu:24.04

RUN (sed -i 's@//.*archive.ubuntu.com@//mirrors.ustc.edu.cn@g' /etc/apt/sources.list.d/ubuntu.sources && \
    sed -i 's@//.*security.ubuntu.com@//mirrors.ustc.edu.cn@g' /etc/apt/sources.list.d/ubuntu.sources) || \
    (echo "deb https://mirrors.ustc.edu.cn/ubuntu/ noble main restricted universe multiverse" > /etc/apt/sources.list && \
    echo "deb https://mirrors.ustc.edu.cn/ubuntu/ noble-updates main restricted universe multiverse" >> /etc/apt/sources.list && \
    echo "deb https://mirrors.ustc.edu.cn/ubuntu/ noble-security main restricted universe multiverse" >> /etc/apt/sources.list)

RUN apt-get update
RUN apt-get install -y --no-install-recommends \
    wget \
    curl \
    file \
    tmux \
    xz-utils \
    python3 \
    python3-pip \
    python3-venv \
    binwalk \
    foremost \
    exiftool



RUN python3 -m venv .venv
RUN .venv/bin/pip install \
    pwntools \
    pycryptodome

RUN curl -qsL 'https://install.pwndbg.re' | sh -s -- -t pwndbg-gdb
RUN ln -s /usr/local/bin/pwndbg /bin/gdb

RUN echo "source /.venv/bin/activate" >> /root/.bashrc

WORKDIR /workspace

CMD ["/bin/bash"]