FROM openvino/ubuntu18_runtime:2020.4 

USER root

# Copy LVA extension specific files
RUN mkdir /app
COPY ./app/*.py /app/
COPY ./app/grpc-autogen/*.py /app/
COPY ./app/gst-lva-extension/*.* /app/

# Install gstreamer-1.0-dev
RUN apt-get update -y && \
    apt-get install -y --no-install-recommends libgstreamer1.0-dev 

# Build LVA GST library
RUN mkdir -p /app/build && \
    cd /app/build && \
    cmake .. && \
    make

# Install Git and clone OMZ (OpenVINO Model Zoo)
RUN apt-get update -y && \ 
    apt-get install -y --no-install-recommends git && \
    git clone https://github.com/openvinotoolkit/open_model_zoo $INTEL_OPENVINO_DIR/omz && \
    apt-get clean && \
    apt-get purge -y --auto-remove git

# Copy model list file
RUN mkdir -p /data/models
COPY ./models/models.lst /data/models

# Install required python packages 
RUN pip3 install requests pyyaml protobuf grpcio && \
    apt-get clean

# Download models
RUN cd $INTEL_OPENVINO_DIR/omz/tools/downloader && \
    python3 downloader.py --list /data/models/models.lst -o /data/models

# Copy model proc files
# There may be more at https://github.com/opencv/gst-video-analytics/tree/master/samples/model_proc
RUN mkdir -p /data/model_procs
COPY ./models/model_proc/*.json /data/model_procs/

# Install additional python packages
RUN pip3 install numpy flask pillow gunicorn && \
    apt-get clean

# Install runit, nginx
RUN apt-get update -y && \
    apt-get install --no-install-recommends -y wget runit nginx

# Install Nchan module. For details goto http://nchan.io
RUN apt-get update -y && \
    apt-get install -y libnginx-mod-nchan

# Copy nginx config file
COPY ./app/nginx/lva_grpc_app.conf /etc/nginx/sites-available

# Copy flask app
COPY ./app/nginx/lva_grpc_app.py /app

# Setup runit file for nginx and gunicorn
RUN mkdir /var/runit && \
    mkdir /var/runit/nginx && \
    /bin/bash -c "echo -e '"'#!/bin/bash\nexec nginx -g "daemon off;"\n'"' > /var/runit/nginx/run" && \
    chmod +x /var/runit/nginx/run && \
    ln -s /etc/nginx/sites-available/lva_grpc_app.conf /etc/nginx/sites-enabled/ && \
    rm -rf /etc/nginx/sites-enabled/default && \
    mkdir /var/runit/gunicorn && \
    /bin/bash -c "echo -e '"'#!/bin/bash\nexec gunicorn -b 127.0.0.1:8000 --chdir /app lva_grpc_app:app\n'"' > /var/runit/gunicorn/run" && \
    chmod +x /var/runit/gunicorn/run

EXPOSE 80
EXPOSE 5001

# Run startup script that initialized OpenVINO environment variables and starts the LVA gRPC extension server
WORKDIR /app
COPY ./app/start.sh /app
RUN chmod +x /app/start.sh
CMD exec /app/start.sh

