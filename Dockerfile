# docker build -t zelbanna/rims:latest -t zelbanna/rims:9.0 .

# Compile and add easysnmp required libs 
FROM python:3.11.9-bookworm AS compile-image
# mariadb-client
RUN apt-get update && apt-get -y install libsnmp-dev
RUN pip install --user pymysql pythonping paramiko influxdb_client easysnmp

#
FROM python:3.11.9-slim-bookworm AS build-image
RUN apt-get update && apt-get -y install libsnmp-base libsnmp40
COPY --from=compile-image /root/.local /root/.local

EXPOSE 8080
EXPOSE 8081
# Set the working directory in the container
WORKDIR /rims

# Copy the current directory contents into the container at /rims
COPY . /rims
COPY ./config /etc/rims

# Command to run the Python script
ENV PATH=/root/.local/bin:$PATH
CMD ["/rims/daemon.py"]
