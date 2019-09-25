#!/usr/bin/env python3
import os
from doatFunctions import *
import subprocess
import configparser

#Print startup message
doat_motd()

#Check system setup
sys_check()

#Read and check config options from config file
config = configparser.ConfigParser()
config.read('config.cfg')
dpdkcmd=config['DOAT']['dpdkcmd']
if dpdkcmd is not None:
    print("DPDK app launch command:",dpdkcmd)
else:
    sys.exit("No DPDK command was specified (dpdkcmd in config.cfg), ABORT!")
startuptime=int(config['DOAT']['startuptime'])
if startuptime is not None:
    print("Startup time for DPDK App:",startuptime)
else:
    sys.exit("No startup time was specified (startuptime in config.cfg), ABORT!")
testruntime=int(config['DOAT']['testruntime'])
if testruntime is not None:
    print("Startup time for DPDK App:",testruntime)
else:
    sys.exit("No test run time was specified (testruntime in config.cfg), ABORT!")
testcore=int(config['CPU']['testcore'])
testsocket=int(subprocess.check_output("cat /proc/cpuinfo | grep -A 18 'processor\s\+: "+str(testcore)+"' | grep 'physical id' | head -1 | awk '{print substr($0,length,1)}'", shell=True))
if testcore is not None:
    print("Test software core:",testcore,"(Socket: "+str(testsocket)+")")
else:
    sys.exit("No test core was specified (testcore in config.cfg), ABORT!")
appmasterenabled=True
appmaster=int(config['CPU']['appmaster'])
appmastersocket=int(subprocess.check_output("cat /proc/cpuinfo | grep -A 18 'processor\s\+: "+str(appmaster)+"' | grep 'physical id' | head -1 | awk '{print substr($0,length,1)}'", shell=True))
if appmaster is not None:
    print("DPDK app master core:",appmaster,"(Socket: "+str(appmastersocket)+")")
else:
    appmasterenabled=False
    print("DPDK app has no master core")
appcores=[int(e) for e in (config['CPU']['appcores']).split(",")]
appcoresno=len(appcores)
if appcores is not None:
    print("DPDK app has",appcoresno,"cores:",appcores)
else:
    sys.exit("No DPDK app cores were specified (appcores in config.cfg), ABORT!")
appcoressockets=[]
appsocket=None
for x in appcores:
    appcoressockets.append(int(subprocess.check_output("cat /proc/cpuinfo | grep -A 18 'processor\s\+: "+str(appmaster)+"' | grep 'physical id' | head -1 | awk '{print substr($0,length,1)}'", shell=True)))
if appmasterenabled:
    if all(x == appcoressockets[0] for x in appcoressockets) and appmastersocket == appcoressockets[0]:
        appsocket=appcoressockets[0]
        print("DPDK app running on socket",appsocket)
    else:
        sys.exit("DPDK app cores and master core must be on the same socket, ABORT!")
else:
    if all(x == appcoressockets[0] for x in appcoressockets):
        appsocket=appcoressockets[0]
        print("DPDK app running on socket",appsocket)
    else:
        sys.exit("DPDK app cores must be on the same socket, ABORT!")

print("Starting Process")
FNULL = open(os.devnull, 'w')
proc = subprocess.Popen(dpdkcmd, stdout=FNULL, stderr=subprocess.STDOUT, shell=True, preexec_fn=os.setsid) 
testpid = proc.pid

if check_pid(testpid):
    print("Test process starting")
else:
    sys.exit("Test process failed to start, ABORT!")

print("Allow application to startup . . .")
progress_bar(startuptime)

if proc.poll() is not None:
    sys.exit("Application died or failed to start, ABORT!")
else:
    print("Test process started successfully, , PID: ",testpid)

print("Running Test . . .")
progress_bar(testruntime)

if proc.poll() is None:
    print("SUCCESS: Test process is still alive after test")
else:
    print("ERROR: Test process died during test")

print("Killing test process")
kill_group_pid(testpid)

print("Exiting . . .")