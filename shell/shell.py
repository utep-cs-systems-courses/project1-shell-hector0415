#! /usr/bin/env python3

import os, sys, re


def main():
    while True:
        keyboard = input(sys.ps1)
        
        if keyboard == "": #no input
            pass
        
        elif keyboard.strip() == "exit": #leave shell
            sys.exit(0)

        elif "cd" in keyboard: #change directory
            change_directory(keyboard)

        else: #not predefined command
     
            rc = os.fork()
            
            if rc < 0:                      #could not fork
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
#end of main
                
def execute_command(command):
    fork_value = os.fork()
            
    args = command.split()
    
    if fork_value < 0:                      #could not fork
        os.write(2, ("forking failed, returning %d\n" % fork_value).encode())
        sys.exit(1)
    elif fork_value == 0:                   # child
        
        for dir in re.split(":", os.environ['PATH']): # try each directory in the path
            program = "%s/%s" % (dir, args[0])
            try:
                os.execve(program, args, os.environ) # try to exec program
            except FileNotFoundError:             # ...expected
                pass                              # ...fail quietly
    
        os.write(2, ("Could not excecute the following command \"%s\"\n" % command).encode())
        sys.exit(1)                 # terminate with error if execve could not run program
        
    else:                           # parent
        child = os.wait()
        os.write(1, ("terminated with exit code %d\n" %child[1]).encode())
            
def change_directory(command):
    cmd = command.split(' ',1)
    os.chdir(cmd[1])

def parse_pipe(command):
    cmd1 = None
    cmd2 = None
    cmd1,cmd2 = command.split('|',1)
    
    return cmd1.strip(),cmd2.strip()
#end of parsePipe

def parse_redirects(command):
    cmd = ""
    fileIn = None
    fileOut = None
    
    if '>' in command:
        cmd,fileOut = command.split('>',1)
    
    if '<' in cmd:
        cmd, fileIn = cmd.split('<', 1)
    
    elif fileOut != None and '<' in fileOut:
        fileOut, fileIn = fileOut.split('<', 1)
        
    return cmd.strip(),fileIn.strip(),fileOut.strip()
#end of parseReDirs

try:
    sys.ps1 = os.environ['PS1']
except KeyError:
    sys.ps1 = '$ '

if sys.ps1 is None:
    sys.ps1 = '$ '

if __name__ == '__main__':
    main()