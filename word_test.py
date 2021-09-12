import os
import sys
from time import sleep
import time
import hashlib
from pyhashcat import Hashcat

hc = Hashcat()

def get_hashcat():
    return hc


def run_hashcat(input_hash):

    print "[+] Testing Hashcat..."

    hc = Hashcat()

    print "[+] Hashcat initialized with id: ", id(hc)
    print input_hash
    hc.hash = input_hash
    hc.quiet = True
    hc.potfile_disable = True
    hc.outfile = "./outfile.txt"
    hc.attack_mode = 0
    hc.hash_mode = 0
    hc.workload_profile = 3
    hc.dict1 = "../Wordlists/princeCombo.txt"

    print "[+] Running hashcat..."
    crackedFlag = False

    if hc.hashcat_session_execute() >= 0:
        while True:
            if hc.status_get_status_string() == "Cracked":
                print "Password has been cracked."
                print "Number of passwords tried: ", hc.status_get_progress_cur_relative_skip(), " out of ", hc.status_get_progress_end_relative_skip()
                print "Time for Hashcat to crack password (ms): ", hc.status_get_msec_running()
                crackedFlag = True
                break;
            if hc.status_get_status_string() == "Exhausted":
                print "Hashcat has exhausted dictionary."
                break;
        #sleep(2)

        #if crackedFlag:
         #   with open(hc.outfile, 'r') as f:
          #      f.seek(-2, os.SEEK_END)
           #     while f.read(1) != b"\n":
            #        f.seek(-2, os.SEEK_CUR)
             #   password = f.readlines()[-1]
           # print hc.hash, " : ", password.split(hc.separator)[1].strip('\n')
        #else:
         #   print "Password was not found."
    else:
        print "STATUS: ", hc.status_get_status_string()

    sleep(5)
