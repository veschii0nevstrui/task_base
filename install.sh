#!/bin/bash

sudo apt-get update -y
sudo apt-get install python3 -y
sudo apt-get install python3-pip -y
sudo apt-get install python3-sqlalchemy -y

sudo apt-get install mariadb-server mariadb-client -y

pip3 install flask --user
pip3 install flask_login --user
pip3 install flask_wtf --user
pip3 install pymysql --user

/etc/init.d/mysql start

sudo mysql < dp.sql