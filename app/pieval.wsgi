#!/usr/bin/python
import sys
# assuming this project is checked out/built in apache dirs as root or with sudo
sys.path.insert(0,"/var/www/pieval/")
from app import app as application
