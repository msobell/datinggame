#! /usr/bin/env python
"""
Solves the dating game problem
Usage: client.py <input file>
"""

import sys
import os
import time
import socket
import string
import random
import copy

HOST = 'localhost'
PORT = 20000
t_time = time.time()
N = 10
file = "Person.txt"
role = ""
start_time = time.time()

class InfoGain:
    def __init__(self, N):
        self.N = N
        self.vector = []
        self.input = []

    def export(self):
        estring = ""
        count = 0
        for v in self.vector:
            estring += v
            count += 1
            if count < self.N:
                estring += ":"
        self.vector = []
        return estring

    def make_candidate(self):
        for i in range(0,self.N):
            # TODO - do somethin wit it
            self.vector.append( "%.2f" % random.random() )

        return self.export()

    def printInput(self):
        for i in self.input:
            print i


def usage():
    sys.stdout.write( __doc__ % os.path.basename(sys.argv[0]))

## From:
## Charles J. Scheffold
## cjs285@nyu.edudef SReadLine (conn):
def SReadLine (conn):
    data = ""
    while True:
        c = conn.recv(1)
        if not c:
            time.sleep(1)
            break
        data = data + c
        if c == "\n" or c == "\r":
            print data
            break
    return data

if __name__ == "__main__":

    if len(sys.argv) != 2:
        usage()
        sys.exit(1)

    # Open connection to evasion server
    s = socket.socket (socket.AF_INET, socket.SOCK_STREAM)
    s.connect ((HOST, PORT))
    print "Connected to", HOST, "port", PORT

    ID = sys.argv[1]

    s.send(ID + '\n')

    # Read status line
    data = SReadLine (s)
    line = string.strip (data)

    if "Person" in ID:
        role = "PERSON"
    elif "Matchmaker" in ID:
        role = "MATCHMAKER"

    print "Role:",role

    while "PERSON" in role and line is not None:
        print "Line:",line
        if "N:" in line:
            parse = line.split(":")
            N = int(parse[1])
            print "Read N:",N
            s.send(file + '\n')
            print "Sent attributes file"
        if "ATTRIBUTES" in line:
            if "DISCONNECT" in SReadLine(s):
                break
        data = SReadLine (s)
        line = string.strip (data)

    while "MATCHMAKER" in role:
        data = SReadLine (s)
        line = string.strip (data)
        print "Line:",line
        if line is None:
            break
        if line[0:2] == "N:":
            parse = line.split(":")
            N = int(parse[1])
            print "N:",N
            ig = InfoGain(N)

            for i in range(0,20):
                inputLine = SReadLine(s)
                # TODO - do somethin wit it
                ig.input.append( string.strip(inputLine) )

            ig.printInput()
            print "done printing from ig class"

        if "SCORE:" in line:
            # SCORE:PREVIOUS CANDIDATE'S SCORE:TOTAL SCORE:# OF CANDIDATES USED
            candidate = ""

            candidate = ig.make_candidate()

            print "Candidate vector:",candidate
            s.send(candidate + '\n')

        if "DISCONNECT" in line:
            break

        if "IDEAL CANDIDATE FOUND" in line \
               or "NO MORE CANDIDATES" in line:
            print SReadLine(s)
            break

    # Poof!
    s.close ()

    print "Time: ",round(time.time() - start_time)
