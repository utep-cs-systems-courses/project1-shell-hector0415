#! /usr/bin/env python3

import os, sys, re

pid = os.getpid()

while True:
    
    keyboard = input("$")
    
    if(keyboard == "exit"):
        sys.exit(0)
    else:
        
        os.write(1, ("About to fork (pid:%d)\n" % pid).encode())
        
        rc = os.fork()
        
        if rc < 0:
            os.write(2, ("fork failed, returning %d\n" % rc).encode())
            sys.exit(1)
        elif rc == 0:                   # child
            #os.write(1, ("I am child.  My pid==%d.  Parent's pid=%d\n" % (os.getpid(), pid)).encode())
            
            args = keyboard.split()
            for dir in re.split(":", os.environ['PATH']): # try each directory in the path
                program = "%s/%s" % (dir, args[0])
                try:
                    os.execve(program, args, os.environ) # try to exec program
                except FileNotFoundError:             # ...expected
                    pass                              # ...fail quietly
        
            os.write(2, ("Child:    Could not exec %s\n" % args[0]).encode())
            sys.exit(1)                 # terminate with error if execve could not run program
            
        else:                           # parent
            child = os.wait()
            os.write(1, ("Parent: Child %d terminated with exit code %d\n" %child).encode())