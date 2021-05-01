#! /home/stepan/twitter/bin/python3
import sys

if "/home/stepan/stranka" not in sys.path:
	sys.path.append('/home/stepan/stranka/')
	sys.path.append("/home/stepan/twitter/lib/python3.8/site-packages")
from web import server as application
