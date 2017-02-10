#!/usr/bin/env python3
# Data to be logged:
# System
# -Battery voltage
# -Comms loss
# -Time
# Drivetrain
# -L/R encoder counts
# -Average encoder count
# -Voltage of all Talons
# Shooters
# -RPMs
# -PID output
# -PID enabled
# -PID setpoint
# -Voltage of all Talons
# Feeders
# -RPMs
# -PID output
# -PID enabled
# -PID setpoint
# -Voltage of all Talons
# Climber/Intake
# -Voltage of all Talons
# Vision
# -centerX
# -lambda
# -delta
# -midpoint
# -number of contours

import csv
from datetime import datetime
import logging
from networktables import NetworkTables
import os
import sys
import time

# False after the first time NetworkTables connects
first_connect = True
# Directory the log files are stored in
log_dir = 'logs/'
# True when data is received for the first time
data_received = False
# Time since
downtime = time.time()
# True when headers have been created in the logfile
headers = False
# number of dots for the stylish printer function
num_dots = 0
# Time to wait before restarting, in seconds
wait_time = 15
# Variable to monitor for changes
watched_var = 'time'


# Is run when connected or disconnected from NetworkTables server
def connection_listener(connected, info):
    global data_received, sd
    if connected:
        print('\nCONNECTED TO ROBOT')
    else:
        print('\nLOST CONNECTION TO ROBOT')
        sd.delete(watched_var)
        # Reset data_received to make program check for watched_var when reconnected
        data_received = False


# Returns an array of all the keys in the table
def get_keys():
    return sd.getKeys()


# Prints an error if table doesn't contain watched_var
def watched_var_exists():
    if NetworkTables.isConnected():
        if get_keys():
            if watched_var not in get_keys():
                return False
    return True


# Called every time watched_var is changed
def watched_var_changed(table, key, value, isNew):
    global downtime, data_received
    data_received = True
    downtime = time.time()
    write_table(table)


# Write all current values in table to logfile
def write_table(table):
    global headers, writer, watched_var
    sorted_table = sorted(table.getKeys())
    leading_var = sorted_table.pop(sorted_table.index(watched_var))
    sorted_table.insert(0, leading_var)

    # if first time writing, create headers
    if not headers:
        writer.writerow(sorted_table)
        headers = True

    # build a list of values
    line = [table.getValue(key) for key in sorted_table]
    # Write line to file
    writer.writerow(line)


# Prints 'Logging' in a stylish way
def print_logging_stylish():
    global num_dots
    if num_dots == 0:
        print('\r          ', end='')
    print('\rLogging' + num_dots * '.', end='')
    num_dots += 1
    if num_dots > 3:
        num_dots = 0


def get_downtime():
    """:returns: the time since the program was last connected to a NetworkTables instance"""
    return round(time.time() - downtime)


def get_logfile_path():
    """:returns: the path of the current log file"""
    return os.path.dirname(__file__) + '/' + logfile_name


if __name__ == '__main__':

    print('Starting SharkLogger...')
    print('===========================================================')

    logging.basicConfig(level=logging.ERROR)

    # For actual robot
    NetworkTables.initialize(server='roboRIO-226-FRC.local')

    # For testing
    # NetworkTables.initialize(server='127.0.0.1')

    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
        print('Created directory:', log_dir)

    while True:

        data_received = False
        downtime = time.time()
        first_connect = True
        headers = False
        num_dots = 0
        timed_out = False

        # Open new csv file & csv writer
        logfile_name = log_dir + datetime.now().strftime('%Y%m%d-%H%M%S') + '.csv'
        logfile = open(logfile_name, 'w', newline='')
        writer = csv.writer(logfile, quoting=csv.QUOTE_ALL)
        print('Created file:', logfile_name)

        # Add connection listener
        NetworkTables.addConnectionListener(connection_listener, immediateNotify=True)
        # Get table from robot
        sd = NetworkTables.getTable('SmartDashboard')
        # Listen for changes in watched_var
        sd.addTableListener(watched_var_changed, key=watched_var)

        while True:
            # Only run on initial startup
            if not NetworkTables.isConnected() and first_connect:
                s = True
                while True:
                    if NetworkTables.isConnected():
                        first_connect = False
                        break
                    # Print waiting message stylishly
                    if s:
                        print('\rWaiting for initial data...', end='')
                    else:
                        print('\r                           ', end='')
                        print('\rWaiting for initial data..', end='')
                    s = not s
                    time.sleep(0.5)
            # Run when disconnected from table
            elif not NetworkTables.isConnected() and not first_connect:
                downtime = time.time()
                while True:
                    if NetworkTables.isConnected():
                        break
                    print('Waiting...', wait_time - get_downtime())
                    if get_downtime() >= wait_time:
                        logfile.close()
                        print('TIMED OUT')
                        break
                    time.sleep(1)
                break
            # Run when connected to table
            elif NetworkTables.isConnected():
                print('Checking for watched var ' + "'" + watched_var + "'" + '...')
                time.sleep(3)
                # Check for watched_var
                if watched_var_exists():
                    print('Done')
                    # If data is received, log
                    if data_received:
                        # log until disconnected
                        while True:
                            # When disconnected, break and move up to waiting loop
                            if not NetworkTables.isConnected():
                                break
                            print_logging_stylish()
                            time.sleep(0.5)
                # If watched_var doesn't exist, print an error and wait for disconnect
                else:
                    logging.error('Error: watched var ' + "'" + watched_var + "'" + ' not found in table!')
                    while True:
                        if not NetworkTables.isConnected():
                            break
                        time.sleep(1)
