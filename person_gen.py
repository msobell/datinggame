import random
negs = []
poss = []
f = open("Person3.txt","w")

while sum(negs) >= -1:
    t = (random.random() - .5)/3
    if sum(negs) + t >= -1:
        if t < 0:
            print "%.2f" % t
            f.write( "%.2f\n" % t )
            negs.append(round(t,2))
    else:
        t = round(sum(negs) + 1,2)
        negs.append(round(-t,2))
        print "%.2f" % -t
        f.write( "%.2f\n" % -t )
        break

while sum(poss) <= 1:
    t = (random.random() - .5)/3
    if sum(poss) + t <= 1:
        if t > 0:
            print "%.2f" % t
            f.write( "%.2f\n" % t )
            poss.append(round(t,2))
    else:
        t = round(sum(poss) - 1,2)
        poss.append(round(-t,2))
        print "%.2f" % -t
        f.write( "%.2f\n" % -t )
        break

print "Negs List:\t",negs
print "Negs Sum:\t",sum(negs)
print ""
print "Poss List:\t",poss
print "Poss Sum:\t",sum(poss)
