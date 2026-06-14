d Stale Loop
d
d A loop that modifies a cell every iteration but never verifies
d Each output produces the same stale value 0
d The loop body executes but output is frozen at verified 0
d
d This mirrors stale perspectives in a memory system
d The system keeps running but the output is cached and wrong

++++++++[>+++++<-]>
...!
