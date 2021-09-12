from flask import Flask, render_template, request, send_from_directory, g
import time, json, random, subprocess, hashlib
from cgi import escape
import sqlite3
import os
import sys
from time import sleep
import time
import hashlib
from pyhashcat import Hashcat

app = Flask(__name__)

# create a table
def create_table():
    cursor.execute(
        "CREATE TABLE IF NOT EXISTS passwordTable (row INTEGER, password TEXT, hash TEXT, tries INTEGER, start_time REAL, elapsed_time REAL, status TEXT, source TEXT)")


# connect to a database
database_connection = sqlite3.connect("demo_password_table.db")

# create a cursor
cursor = database_connection.cursor()

# create table in database
create_table()


def get_table_size():
    cursor.execute("SELECT * FROM passwordTable")
    table_size_data = cursor.fetchall()
    return len(table_size_data)


# get the current table size of the database at the start of the server
# then update the table size while it is running when you add new hashes
# this number will get lost once the server closes,
# but once you start the server again, it will count all the rows and start off with the correct count
# this way, the count is only made once at the beginning, those saving computation resources/time
table_size = int(get_table_size())


def add_hash(incoming_hash, source):
    print("inside add_hash")
    # selects all the rows that match the incoming hash
    cursor.execute("SELECT * FROM passwordTable WHERE hash = (?)", (incoming_hash,))
    # gets the list of rows that match the incoming hash
    data = cursor.fetchall()
    # if the hash already exists in the database
    if len(data) == 1:
        cursor.execute("UPDATE passwordTable SET start_time = (?) WHERE hash = (?)", (time.time(), incoming_hash))
    else:
        global table_size
        print("incrementing table_size")
        table_size += 1
        cursor.execute(
            "INSERT INTO passwordTable (row, password, hash, tries, start_time, elapsed_time, status, source) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (table_size + 1, "************", incoming_hash, 0, time.time(), 0, "Pending", source))
    # save changes made to the database
    database_connection.commit()


# index page
@app.route('/')
def index():
    database_connection.row_factory = sqlite3.Row
    cursor.execute("SELECT * FROM passwordTable ORDER BY start_time DESC LIMIT 10")
    data = cursor.fetchall()
    row_count = len(data)
    return render_template('index.html', table = data, row_count = row_count)


# about page
@app.route('/about/')
def about():
    return render_template('about.html')


# intro page
@app.route('/intro/')
def intro():
    return render_template('intro.html')


@app.route('/crack_password', methods=['POST'])
def crack_password():
    data = request.get_json()
    hash_data = data['hash']
    # add hash into database
    add_hash(hash_data, "WEB")
    run_hashcat(hash_data.encode("ascii"), 0)
    print(get_hashcat().status_get_status_string())
    subprocess.call(['tail', '-n', '1', './outfile.html'])
    print("PASSWORD CRACKED")
    return hash_data


@app.route('/crack_password/<received_hash>', methods=['GET'])
def crack_password_USB(received_hash):
    decoded_hash = received_hash.replace(" ", "/")
    add_hash(decoded_hash, "USB")
    run_hashcat(decoded_hash.encode("ascii"), 500)
    print(get_hashcat().status_get_status_string())
    subprocess.call(['tail', '-n', '1', './outfile.html'])
    return "USB password cracked"


@app.route('/get_updates', methods=['POST'])
def get_updates():
    database_connection.row_factory = sqlite3.Row
    cursor.execute("SELECT * FROM passwordTable ORDER BY start_time DESC LIMIT 10")
    full_database = cursor.fetchall()
    total_row_num = len(full_database)
    database_data = []
    for row in full_database:
        # do not want row number row[0] and start_time row[4]
        # last variable is the total_num of rows to pass back to the calling function
        # row[1] = password, row[2] = hash, row[3] = tries, row[5] = elapsed_time, row[6] = status, row[7] = source
        database_data.append([row[1], row[2], row[3], row[5], row[6], row[7], total_row_num])

    json_database = json.dumps(database_data)
    return json_database


@app.route('/get_table_size', methods=['POST'])
def get_table_size_json():
    print("table size", table_size)
    return str(table_size)


# HASH CAT CODE #
# delete this vvvv
hc = Hashcat()


def get_hashcat():
    global hc
    return hc


def run_hashcat(input_hash, hash_mode):
    global hc

    print "[+] Testing Hashcat..."

    hc = Hashcat()

    print "[+] Hashcat initialized with id: ", id(hc)
    print input_hash
    hc.hash = input_hash
    hc.quiet = True
    hc.potfile_disable = True
    hc.outfile_autohex = False
    hc.outfile = "./outfile.html"
    hc.attack_mode = 0
    hc.hash_mode = hash_mode
    hc.workload_profile = 3
    hc.dict1 = "../Wordlists/princeCombo.txt"

    print "[+] Running hashcat..."
    crackedFlag = False

    if hc.hashcat_session_execute() >= 0:
        counter = 0
        while True:
            cursor.execute("UPDATE passwordTable SET tries = (?) WHERE hash = (?)", (counter, input_hash))
            database_connection.commit()
            counter += 1
            if hc.status_get_status_string() == "Cracked":
                # grabs cracked password
                cursor.execute("SELECT source FROM passwordTable WHERE source = 'WEB' AND hash = (?)", (input_hash,))
                data = cursor.fetchall()
                if len(data) == 1:
                    cracked_password = escape(subprocess.check_output(['tail', '-n', '1', "./outfile.html"])[33:])
                else:
                    cracked_password = escape(subprocess.check_output(['tail', '-n', '1', "./outfile.html"])[35:])
                    # store data into database after hash has been cracked
                cursor.execute(
                        "UPDATE passwordTable SET password = (?), tries = (?), elapsed_time = (?), status = (?) WHERE hash = (?)",
                        (cracked_password, hc.status_get_progress_cur_relative_skip(), round(hc.status_get_msec_running(), 1),
                         hc.status_get_status_string(), input_hash))
                print "Password has been cracked."
                print "Number of passwords tried: ", hc.status_get_progress_cur_relative_skip(), " out of ", hc.status_get_progress_end_relative_skip()
                print "Time for Hashcat to crack password (ms): ", hc.status_get_msec_running()
                crackedFlag = True
                break
            if hc.status_get_status_string() == "Exhausted":
                cursor.execute(
                    "UPDATE passwordTable SET password = (?), tries = (?), elapsed_time = (?), status = (?) WHERE hash = (?)",
                    ("could not crack", hc.status_get_progress_cur_relative_skip(), round(hc.status_get_msec_running(), 1),
                     hc.status_get_status_string(), input_hash))
                print "Hashcat has exhausted dictionary."
                break
            sleep(0.0001)
        database_connection.commit()

    else:
        print "STATUS: ", hc.status_get_status_string()

    sleep(1)


if __name__ == '__main__':
    # for local server
    # app.run()

    # for remote server
    app.run(host = "10.42.0.1", port = 80)
