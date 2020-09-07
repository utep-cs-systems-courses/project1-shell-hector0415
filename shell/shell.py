#! /usr/bin/env python3

import os, sys, re

pid = os.getpid()

while True:
    
    keyboard = input("$")
    
    if(keyboard == "exit"):
        sys.exit(0)
    else:
 
        rc = os.fork()
        
        if rc < 0:
            os.write(2, ("forking failed, returning %d\n" % rc).encode())
            sys.exit(1)
        elif rc == 0:                   # child
            
            args = keyboard.split()
            for dir in re.split(":", os.environ['PATH']): # try each directory in the path
                program = "%s/%s" % (dir, args[0])
                try:
                    os.execve(program, args, os.environ) # try to exec program
                except FileNotFoundError:             # ...expected
                    pass                              # ...fail quietly
        
            os.write(2, ("Child says: Could not excecute the following command \"%s\"\n" % keyboard).encode())
            sys.exit(1)                 # terminate with error if execve could not run program
            
        else:                           # parent
            child = os.wait()
            os.write(1, ("Parent says: Child %d terminated with exit code %d\n" %child).encode())
