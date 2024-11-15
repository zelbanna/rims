# docker build -t zelbanna/rims:latest -t zelbanna/rims:9.0 .

# Compile and add easysnmp required libs 
FROM python:3.12.6-bookworm AS compile-rims-dependencies
# mariadb-client
RUN apt-get update && apt-get -y install libsnmp-dev
RUN pip install --user pymysql pythonping paramiko influxdb_client easysnmp

#
FROM python:3.12.6-slim-bookworm AS build-rims-image
RUN apt-get update && apt-get -y install libsnmp-base libsnmp40
COPY --from=compile-rims-dependencies /root/.local /root/.local
COPY . /rims
COPY ./config /etc/rims

WORKDIR /rims

EXPOSE 8080
EXPOSE 8081

# Command to run the Python script
ENV PATH=/root/.local/bin:$PATH
CMD ["/rims/daemon.py"]
#CMD ["/bin/bash"]
