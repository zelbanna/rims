#!/bin/bash

openssl genrsa -aes256 -out ../ca/CA-key.pem 4096
openssl rsa -in ../ca/CA-key.pem -outform PEM -pubout -out ../ca/CA.pub
openssl req -new -key ../ca/CA-key.pem -x509 -days 1825 -out ../ca/CA-cert.pem
openssl x509 -outform der -in ../ca/CA-cert.pem -out ../ca/CA-cert.crt
cp ../ca/CA-cert.crt ../site/CA-cert.crt
cp ../ca/CA-cert.crt ../static/CA-cert.crt

