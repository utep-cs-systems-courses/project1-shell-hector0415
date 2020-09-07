#! /usr/bin/env python3

import os, sys

pid = os.getpid()

while True:
    
    kybrd = input("$")
    
    if(kybrd == "exit"):
        break
    else:
        
        os.write(1, ("About to fork (pid:%d)\n" % pid).encode())
        
        rc = os.fork()
        
        if rc < 0:
            os.write(2, ("fork failed, returning %d\n" % rc).encode())
            sys.exit(1)
        elif rc == 0:                   # child
            os.write(1, ("I am child.  My pid==%d.  Parent's pid=%d\n" % (os.getpid(), pid)).encode())
            os.write(1, ("Oh no! I must be going now...").encode())
            #<<exec code goes here>>
            
            sys.exit(0) # exit(0) if we were able to run the program. Change later to 
                        #dynamically return the proper exit value if we weren't able
                        #to run the program.
            
        else:                           # parent
            os.write(1, ("I am parent.  My pid=%d.  Child's pid=%d\n" % (pid, rc)).encode())
