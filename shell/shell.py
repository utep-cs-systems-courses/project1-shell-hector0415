#! /usr/bin/env python3

import os, sys, re


def main():
    while True:
        os.write(1, sys.ps1.encode())
        keyboard = os.read(0,1024).decode().strip()
        
        if keyboard == "": #no input
            pass
        
        elif keyboard.strip() == "exit": #leave shell
            sys.exit(0)
            break

        elif "cd" in keyboard: #change directory
            change_directory(keyboard)

        else: #not predefined command
            execute_keyboard(keyboard)
#end of main
                
def execute_keyboard(command):
    fork_value = os.fork()
    
    wait = True
    if command[-1] == '&': #check if running in background
        wait = False
        command = command[:-1] #remove the & from the command
    
    if fork_value < 0:                      #could not fork
        os.write(2, ("forking failed, returning %d\n" % fork_value).encode())
        sys.exit(1)
    elif fork_value == 0:                   # child
        if '|' in command:
            #pipe execute
            command_one, command_two = parse_pipe(command)
            
            pipe_read,pipe_write = os.pipe() #create pipe
            
            std_in = os.dup(0) #make copies of both fd 0 and fd 1
            std_out = os.dup(1)
            
            os.dup2(pipe_write,1) #replace std out with write pipe
            execute_command(command_one) #run first command
            os.dup2(pipe_read,0) #replace std in with read pipe
            os.dup2(std_out,1) #put std out back in fd 1
            execute_command(command_two) #run second command
            os.dup2(std_in,0) #put std in back in fd 0
            
            os.close(std_in)
            os.close(std_out)
            os.close(pipe_read)
            os.close(pipe_write)
            
        else:
            #non-pipe execute
            command,file_in,file_out = parse_redirects(command)
            
            if file_in != "": #open and redirect std in if needed
                std_in = os.dup(0)
                fd_fin = os.open(file_in, os.O_RDONLY)
                os.dup2(fd_fin,0)
            if file_out != "": #open and redirect std out if needed
                std_out = os.dup(1)
                fd_fout = os.open(file_out, os.O_CREAT | os.O_WRONLY)
                os.dup2(fd_fout, 1)
                
            execute_command(command)
            
            if file_in is not None:
                os.close(std_in)
                os.close(fd_fin)
            if file_out is not None:
                os.close(std_out)
                os.close(fd_fout)
        
    else:                           # parent
        if wait:
            child = os.wait()
            #if child[1] != 0:
            #    os.write(2, ("terminated with exit code %d\n" %child[1]).encode())
        return False
        
            
def execute_command(command):
    args = command.split()
    
    for dir in re.split(":", os.environ['PATH']): # try each directory in the path
            program = "%s/%s" % (dir, args[0])
            try:
                os.execve(program, args, os.environ) # try to exec program
            except FileNotFoundError:             # ...expected
                pass                              # ...fail quietly
                
    #os.write(2, ("Could not excecute the following command \"%s\"\n" % command).encode())
    sys.exit(1)                 # terminate with error if execve could not run program
        
        
def change_directory(command):
    cmd = command.split(' ',1)
    if len(cmd) > 1:
        os.chdir(cmd[1])
    #else:
       # os.write(1,("No directory was specified, nothing was done").encode())
#end of change_directory

def parse_pipe(command):
    cmd1,cmd2 = command.split('|',1)
    return cmd1.strip(),cmd2.strip()
#end of parse_pipe

def parse_redirects(command):
    cmd = ""
    fileIn = ""
    fileOut = ""
    
    if '>' not in command and '<' not in command: #when no redirects found
        return command.strip(),fileIn,fileOut
    
    if '>' in command and '<' not in command:
        cmd,fileOut = command.split('>',1)
        return cmd.strip(),fileIn.strip(),fileOut.strip()
    
    if '<' in command and '>' not in command:
        cmd,fileIn = command.split('<',1)
        return cmd.strip(),fileIn.strip(),fileOut.strip()
    
    if '>' in command:
        cmd,fileOut = command.split('>',1)
    
    if '<' in cmd:
        cmd, fileIn = cmd.split('<', 1)
    
    elif fileOut != None and '<' in fileOut:
        fileOut, fileIn = fileOut.split('<', 1)
        
    return cmd.strip(),fileIn.strip(),fileOut.strip()
#end of parse_redirects


if __name__ == '__main__':
    try:
        sys.ps1 = os.environ['PS1']
    except KeyError:
        sys.ps1 = '$ '
    if sys.ps1 is None:
        sys.ps1 = '$ '

    main()
