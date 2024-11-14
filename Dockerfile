# docker build -t rims:9.0 .
# Use Python 3.11 as base image, -slim
FROM python:3.11

RUN apt-get update && apt-get -y install libsnmp-dev mariadb-client
RUN pip install pymysql paramiko influxdb_client easysnmp

# RUN pip install easysnmp
EXPOSE 8080
EXPOSE 8081

# Set the working directory in the container
WORKDIR /rims

# Copy the current directory contents into the container at /rims
COPY . /rims
COPY ./config /etc/rims

# Command to run the Python script
CMD ["/rims/daemon.py"]
