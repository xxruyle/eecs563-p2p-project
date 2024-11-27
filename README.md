# EECS 563 - Project 2: File Sharing Platform
This is an implementatin of the project description for the File Sharing Platform for EECS 563 at KU 

## Usage 
The implementation can be tested using 3 clients on the same machine 


Run python main.py in the project root directory 

The user should see the following prompt: 
```
❯ python3 main.py 
start tracker (t)
send(s)
file request (f)
register (r)?

```

NOTE: Before sending or receiving a file, the user must login (register (r), if they already haven't)
- One client should have the tracker started (t)
- Another client should send a file to the tracker (s)
- Another client should receive a file from the tracker (f)
- If the file info exists in the tracker, the file will be downloaded in the project root directory. The filename has a random number [0, 100000] assigned to it as a prefix. 
