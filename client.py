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
file = "/home/max/heuristics/datinggame/Person.txt"
role = ""
start_time = time.time()

class InfoGain:
    def __init__(self, N):
        self.N = N
        self.input = []
        # Gt (gradient) = gradient
        self.gradient = []*N
        # candidates = self.input
        self.candidates = self.input
        self.candidate = []
        self.weights = []*N


    def export(self):
        estring = ""
        count = 0
        for v in self.candidate:
            if v > 0:
                estring += "1"
            else:
                estring += "0"
            count += 1
            if count < self.N:
                estring += ":"
        return estring

    def make_candidate(self):
        self.candidate = self.score_input()

    def score_input(self):
        """
        from http://cs.nyu.edu/courses/fall10/G22.2965-001/graddesc.html

        Until some stopping condition 
            Gt = vector of length n, initialized to all 0s
            foreach candidate c
                dotprod = sum_i(xc[i]*wt[i])
                diff = dotprod - yc
                foreach gradient index i
                    Gt,i =  Gt,i + diff * xc,i
            foreach weight index i
                wt+1,i = wt,i - eta*Gt,i
        """
        # initialize weights to be a random vector of lenght N
        candidates = copy.deepcopy(self.candidates)
        eta = 0.04 #self.find_eta() # small, < 0.1
        weights = []
        gradient = []
        for i in range(0,N):
            sign = 1
            if random.random() < 0.5:
                sign = -1
            if len(weights) <= N:
                weights.append(random.random()*sign)
            else:
                print "Whoops weights too long"
        wsum = float('Inf')
        # we don't want the weights to be changing that drastically
        # each round
        this_eta = eta
        while abs(wsum - sum(weights)) > 0.01:
            if this_eta > 0.002:
                # learn less and less...
                this_eta -= 0.001
            gradient = [0]*N
            print "Weighting gradient:",gradient
            print "Weighting score:",wsum - sum(weights)
            # print "Weights",weights,"Length:",len(weights)
            # print "Self.candidates",self.candidates
            for c in candidates:
                # c = score:v1:v2:...:vn
                score = dot_product(c[1:],weights) # get the score
                cost = score - c[0] # compute the difference
                # print "gradient:",gradient,"\nLength:",len(gradient)
                # print "candidate:",c,"\nLength:",len(c)
                for i in range(0,len(gradient)):
                    gradient[i] += cost*c[i+1]
            scale = max(gradient)
            if scale > 1:
                for i in range(0,len(gradient)):
                    gradient[i] /= scale
                
            wsum = sum(weights)
            for i in range(0,len(weights)):
                weights[i] -= eta*gradient[i]

            # x = raw_input("press any key")
        self.weights = copy.deepcopy(weights)
        # print "returning weights:",weights
        return weights

    def find_eta(self):
        """
        from http://cs.nyu.edu/courses/fall10/G22.2965-001/graddesc.html

	bestCost = inf.
	bestEta n = 0
	foreach eta in eta_range
		currCost = 0
		foreach candidate i
			wi = train(X without xi, Y without yi)
			currCost = currCost + C(wi)
		if currCost < bestCost then 
			bestCost = currCost
			bestEta = eta
        """
        """
        bestCost = float('Inf')
        bestEta = 0
        w = []
        i = 0.0001
        while i <= 0.1:
            currCost = 0
            j = 0
            for c in candidates:
                w = self.score_input(c[:j]+c[j+1:],\
                                     weights[:j]+weights[j+1:])
                currCost += w
                j += 1
            if currCost < bestCost:
                bestCost = currCost
                bestEta = eta
            if i > 0.01:
                i += 0.01
            else:
                i *= 2
        return bestEta
        """
        return 0.01


    # def cost(self, candidates = self.candidates, weights = self.weights):
    #     total_cost = 0
    #     for c in candidates:
    #         total_cost += dot_product(candidates, weights) - 

    def printInput(self):
        for i in self.input:
            print i
        print "done printing from ig class"

def dot_product(a, b):
    return sum([a[i]*b[i] for i in range(len(a))])

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

    ig = None # global
    candidate = []
    prev_candidate = []

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
                t = string.strip(inputLine).split(":")
                for i in range(0,len(t)):
                    t[i]=float(t[i])
                print "Appending t",t
                ig.input.append( t )

            ig.printInput()

        if "SCORE:" in line:
            # SCORE:PREVIOUS CANDIDATE'S SCORE:BEST SCORE:# OF CANDIDATES USED
            # FINAL SCORE:PREVIOUS CANDIDATE'S SCORE:BEST SCORE:ID OF CANDIDATE WITH BEST SCORE
            prev_score = [float(line.split(":")[1])]
            if len(prev_candidate) < N:
                print "this candidate sucks."
                print "prev candidate",prev_candidate
                print "candidate",candidate
            else:
                # we're still learning!
                ig.input.append( prev_score + prev_candidate)

            prev_candidate = copy.deepcopy(candidate) # make sure it's a new list
            ig.make_candidate()
            # print "ig weights",ig.weights
            candidate = copy.deepcopy(ig.weights)
            # print "candidate is now...",candidate
            formatted_candidate = ig.export()
            
            print "Candidate vector:",formatted_candidate
            s.send(formatted_candidate + '\n')

        if "DISCONNECT" in line:
            break

        if "IDEAL CANDIDATE FOUND" in line \
               or "NO MORE CANDIDATES" in line:
            print SReadLine(s)
            sys.exit(0)

    # Poof!
    s.close ()

    print "Time: ",round(time.time() - start_time)
