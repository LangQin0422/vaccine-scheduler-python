import sys
from util.Util import Util
from db.ConnectionManager import ConnectionManager
import pymssql
sys.path.append("../util/*")
sys.path.append("../db/*")


class Caregiver:
    def __init__(self, username, password=None, salt=None, hash=None):
        self.username = username
        self.password = password
        self.salt = salt
        self.hash = hash

    # getters
    def get(self):
        cm = ConnectionManager()
        conn = cm.create_connection()
        cursor = conn.cursor(as_dict=True)

        get_caregiver_details = \
            "SELECT Salt, Hash FROM Caregivers WHERE Username = %s"
        try:
            cursor.execute(get_caregiver_details, self.username)
            for row in cursor:
                curr_salt = row['Salt']
                curr_hash = row['Hash']
                calculated_hash = Util.generate_hash(self.password, curr_salt)
                if not curr_hash == calculated_hash:
                    print("Incorrect password")
                    cm.close_connection()
                    return None
                else:
                    self.salt = curr_salt
                    self.hash = calculated_hash
                    cm.close_connection()
                    return self
        except pymssql.Error as e:
            raise e
        finally:
            cm.close_connection()
        return None

    def get_username(self):
        return self.username

    def get_salt(self):
        return self.salt

    def get_hash(self):
        return self.hash

    def save_to_db(self):
        cm = ConnectionManager()
        conn = cm.create_connection()
        cursor = conn.cursor()

        add_caregivers = "INSERT INTO Caregivers VALUES (%s, %s, %s)"
        try:
            cursor.execute(add_caregivers,
                           (self.username, self.salt, self.hash))
            # you must call commit() to persist your data if you don't set
            # autocommit to True
            conn.commit()
        except pymssql.Error:
            raise
        finally:
            cm.close_connection()

    # Insert availability with parameter date d
    def upload_availability(self, d):
        cm = ConnectionManager()
        conn = cm.create_connection()
        cursor = conn.cursor()

        add_availability = "INSERT INTO Availabilities VALUES (%s , %s)"
        try:
            cursor.execute(add_availability, (d, self.username))
            # you must call commit() to persist your data if you don't set
            # autocommit to True
            conn.commit()
        except pymssql.Error:
            print("Error occurred when updating caregiver availability")
            raise
        finally:
            cm.close_connection()

    # Get caregiver availability with parameter date d
    def get_caregiver_availability(self, d):
        cm = ConnectionManager()
        conn = cm.create_connection()
        cursor = conn.cursor()

        get_availability = "SELECT Username FROM Availabilities WHERE Time = %s"
        try:
            cursor.execute(get_availability, d)
            if cursor.rowcount == 0:
                print("No caregiver is available!")
                return
            for row in cursor:
                print(row[0])
        except pymssql.Error:
            print("Error occurred when getting caregiver availability")
            raise
        finally:
            cm.close_connection()
        return None

    # Get available number of each vaccine
    def get_vaccine_availability(self):
        cm = ConnectionManager()
        conn = cm.create_connection()
        cursor = conn.cursor()

        get_vaccine_availability = "SELECT Name, Doses FROM Vaccines"
        try:
            cursor.execute(get_vaccine_availability)
            if cursor.rowcount == 0:
                print("No available vaccines!")
                return
            print('%-10s' % "Vaccine", '%-10s' % "Dose")
            for row in cursor:
                print('%-10s' % row[0], '%-10d' % row[1])
        except pymssql.Error:
            # print("Error occurred when getting vaccine availability")
            raise
        finally:
            cm.close_connection()
        return None

    # get all the vaccination schedules
    def get_schedules(self):
        cm = ConnectionManager()
        conn = cm.create_connection()
        cursor = conn.cursor()

        get_schedules = "SELECT appointment_id, Vname, Time, Pname FROM Schedules\
            WHERE Cname = %s ORDER BY appointment_id ASC"
        try:
            cursor.execute(get_schedules, self.username)
            print('%-20s' % "Appointment ID", '%-20s' % "Vaccine", '%-20s' % "Time", '%-20s' % "Patient")
            if cursor.rowcount == 0:
                print("No schedules.")
            else:
                for row in cursor:
                    print('%-20d' % row[0], '%-20s' % row[1], '%-20s' % row[2], '%-20s' % row[3])
        except pymssql.Error:
            print("Error occurred when getting schedules")
            raise
        finally:
            cm.close_connection()
        return None
