# docker build -t zelbanna/rims:latest -t zelbanna/rims:9.x.y .
# docker push -a zelbanna/rims

# Compile and add easysnmp required libs 
FROM python:3.12.6-bookworm AS compile-rims-dependencies
# mariadb-client
RUN DEBIAN_FRONTEND=noninteractive apt-get update && apt-get -y install libsnmp-dev
RUN DEBIAN_FRONTEND=noninteractive pip install --user pymysql pythonping paramiko influxdb_client easysnmp

#
FROM python:3.12.6-slim-bookworm AS build-rims-image
RUN apt-get update && apt-get -y install libsnmp-base libsnmp40
COPY --from=compile-rims-dependencies /root/.local /root/.local
COPY . /rims
COPY ./config /etc/rims

WORKDIR /rims
LABEL org.opencontainers.image.authors="Zacharias El Banna  <zacharias@elbanna.se>"
EXPOSE 8080
EXPOSE 8081

# Command to run the Python script
ENV PATH=/root/.local/bin:$PATH
ENTRYPOINT ["/rims/daemon.py"]
# CMD ["-c","/etc/rims/rims.json"]
