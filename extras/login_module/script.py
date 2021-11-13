import hon.masterserver
import sys
re = hon.masterserver.srp_auth(sys.argv[1], sys.argv[2])

print(re['cookie'])
