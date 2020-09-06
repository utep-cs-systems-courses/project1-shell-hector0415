#! /usr/bin/env python3

import os, sys

pid = os.getpid()

os.write(1,("About to fork (pid:%d)\n"%pid).encode())

for i in range(4):
    rc = os.fork()

print(rc)
