# EECS 563 - Project 2: File Sharing Platform
This is an implementatin of the project description for the File Sharing Platform for EECS 563 at KU 

## Requirements 
- Python 

## Usage (Setup) 
The implementation has been tested using 3 clients on the same machine 

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
- If the file info exists in the tracker, the file will be downloaded in the project root directory. 
    - The filename has a random number [0, 100000] assigned to it as a prefix. 

## Example of use  

### Tracker 
Tracker is set up and verifies requests and senders

![Tracker](./screenshots/tracker.png)

### Sender 
Sender sends a file test.txt to the tracker and sends file to requester

![Sender](./screenshots/sender.png)

### File Requester 
File requester requests file test.txt. Tracker verifies this request and a connection is established between sender and requester. Requester downloads the file. 

![Requester](./screenshots/requester.png)

New test.txt file in the directory 

![new test.txt file](./screenshots/received.png)

## Potential Problems 
- Could experience an error if you try to send a file larger than 8kb.
