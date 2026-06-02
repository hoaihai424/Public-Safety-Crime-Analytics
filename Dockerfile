FROM apache/spark:3.5.0-python3

USER root

# 1. Cài đặt các công cụ cần thiết để build Python từ source
RUN apt-get update && \
    apt-get install -y \
    wget \
    build-essential \
    libssl-dev \
    zlib1g-dev \
    libncurses5-dev \
    libnss3-dev \
    libgdbm-dev \
    libreadline-dev \
    libffi-dev \
    libsqlite3-dev \
    libbz2-dev \
    software-properties-common

# 2. Tải và Biên dịch Python 3.11.8 từ Source (Chạy tốt trên ARM64)
WORKDIR /tmp
RUN wget https://www.python.org/ftp/python/3.11.8/Python-3.11.8.tgz && \
    tar -xvf Python-3.11.8.tgz && \
    cd Python-3.11.8 && \
    ./configure --enable-optimizations && \
    make -j $(nproc) && \
    make altinstall

# 3. Cập nhật symlink để python3 trỏ về python3.11
RUN update-alternatives --install /usr/bin/python3 python3 /usr/local/bin/python3.11 1 && \
    update-alternatives --set python3 /usr/local/bin/python3.11

# 4. Cài đặt pip
RUN curl -sS https://bootstrap.pypa.io/get-pip.py | python3.11

# 5. Cài đặt thư viện Python cần thiết
RUN pip3 install --no-cache-dir clickhouse-connect pyspark==3.5.0

# 6. Dọn dẹp (Giảm kích thước image)
RUN rm -rf /tmp/Python-3.11.8* && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Switch back to Spark user
USER 185

# Environment Variables
ENV SPARK_CLASSPATH=/opt/spark/jars-ext/*
ENV PYSPARK_PYTHON=python3
ENV PYSPARK_DRIVER_PYTHON=python3