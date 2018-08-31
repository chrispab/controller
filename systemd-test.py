#!/usr/bin/python2.7
#-------------------------------------------------------------------------------
# Name:        systemd daemon & watchdog test file
# Purpose:
#
# Author:      paulv
#
# Created:     07-05-2016
# Copyright:   (c) paulv 2016
# Licence:     <your licence>
#-------------------------------------------------------------------------------

import sys
import os
from time import sleep
import signal
import subprocess
import socket

init = True

def sd_notify(unset_environment, s_cmd):

    """
    Notify service manager about start-up completion and to kick the watchdog.

    https://github.com/kirelagin/pysystemd-daemon/blob/master/sddaemon/__init__.py

    This is a reimplementation of systemd's reference sd_notify().
    sd_notify() should be used to notify the systemd manager about the
    completion of the initialization of the application program.
    It is also used to send watchdog ping information.

    """
    global init

    sock = None

    try:
        if not s_cmd:
            sys.stderr.write("error : missing s_cmd\n")
            return(1)

        s_adr = os.environ.get('NOTIFY_SOCKET', None)
        if init : # report this only one time
            sys.stderr.write("Notify socket = " + str(s_adr) + "\n")
            # this will normally return : /run/systemd/notify
            init = False

        if not s_adr:
            sys.stderr.write("error : missing socket\n")
            return(1)

        sock = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)
        sock.sendto(s_cmd, s_adr)
        # sendto() returns number of bytes send
        # in the original code, the return was tested against > 0 ???
        if sock.sendto(s_cmd, s_adr) == 0:
            sys.stderr.write("error : incorrect sock.sendto  return value\n")
            return(1)
    except e:
        pass
    finally:
        # terminate the socket connection
        if sock:
            sock.close()
        if unset_environment:
            if 'NOTIFY_SOCKET' in os.environ:
                del os.environ['NOTIFY_SOCKET']
    return(0) # OK


def sig_handler (signum=None, frame = None):
    """
    This function will catch the most important system signals, but NOT a shutdown!
    During testing, you can use this code to see what termination methods are used or filter
    some out.

    This handler catches the following signals from the OS:
        SIGHUB = (1) SSH Terminal logout
        SIGINT = (2) Ctrl-C
        SIGQUIT = (3) ctrl-\
        IOerror = (5) when terminating the SSH connection (input/output error)
        SIGTERM = (15) Deamon terminate (deamon --stop): is coming from deamon manager
    However, it cannot catch SIGKILL = (9), the kill -9 or the shutdown procedure
    """

    try:
        print "\nSignal handler called with signal : {0}".format(signum)
        if signum == 1 :
            sys.stderr.write("Sighandler: ignoring SIGHUB signal : " + str(signum) + "\n")
            return # ignore SSH logout termination
        sys.stderr.write("terminating : python test script\n")
        sys.exit(1)

    except Exception as e: # IOerror 005 when terminating the SSH connection
        sys.stderr.write("Unexpected Exception in sig_handler() : "+ str(e) + "\n")
        subprocess.call(['logger "Unexpected Exception in sig_handler()"'], shell=True)
        return



def main():

    # setup a catch for the following termination signals: (signal.SIGINT = ctrl-c)
    for sig in (signal.SIGTERM, signal.SIGINT, signal.SIGHUP, signal.SIGQUIT):
        signal.signal(sig, sig_handler)

    # get the timeout period from the systemd-test.service file
    wd_usec = os.environ.get('WATCHDOG_USEC', None)
    if wd_usec == None or wd_usec == 0:
        sys.stderr.write("terminating : incorrect watchdog interval sequence\n")
        exit(1)

    wd_usec = int(wd_usec)
    # use half the time-out value in seconds for the kick-the-dog routine to
    # account for Linux housekeeping chores
    wd_kick = wd_usec / 1000000 / 2
    sys.stderr.write("watchdog kick interval = " + str(wd_kick) + "\n")

    try:
        sys.stderr.write("starting : python daemon watchdog and fail test script started\n")
        # notify systemd that we've started
        retval = sd_notify(0, "READY=1")
        if retval <> 0:
            sys.stderr.write("terminating : fatal sd_notify() error for script start\n")
            exit(1)

        # after the init, ping the watchdog and check for errors
        retval = sd_notify(0, "WATCHDOG=1")
        if retval <> 0:
            sys.stderr.write("terminating : fatal sd_notify() error for watchdog ping\n")
            exit(1)

        ctr = 0 # setup a counter to initiate a watchdog fail
        while True :
            if ctr > 5 :
                sys.stderr.write("forcing watchdog fail, restarting service\n")
                sleep(20)

            sleep(wd_kick)
            sys.stderr.write("kicking the watchdog : ctr = " + str(ctr) + "\n")
            sd_notify(0, "WATCHDOG=1")
            ctr += 1


    except KeyboardInterrupt:
        print "\nTerminating by Ctrl-C"
        exit(0)


if __name__ == '__main__':
    main()
