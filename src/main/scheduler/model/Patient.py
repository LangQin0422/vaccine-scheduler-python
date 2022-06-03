import sys
from util.Util import Util
from db.ConnectionManager import ConnectionManager
import pymssql
import random

sys.path.append("../util/*")
sys.path.append("../db/*")


class Patient:
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
            "SELECT Salt, Hash FROM Patients WHERE Username = %s"
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

        add_caregivers = "INSERT INTO Patients VALUES (%s, %s, %s)"
        try:
            cursor.execute(add_caregivers,
                           (self.username, self.salt, self.hash))
            conn.commit()
        except pymssql.Error:
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

        get_vaccine_availability = "SELECT * FROM Vaccines"
        try:
            cursor.execute(get_vaccine_availability)
            if cursor.rowcount == 0:
                print("No available vaccines!")
                return
            print('%-10s' % "Vaccine", '%-10s' % "Dose")
            for row in cursor:
                print('%-10s' % row[0], '%-10d' % row[1])
        except pymssql.Error:
            print("Error occurred when getting vaccine availability")
            raise
        finally:
            cm.close_connection()
        return None

    # make a vaccination schedule with parameter vaccine vaccine,
    # date date
    def make_schedule(self, vaccine, date):
        # check 1: must have enough vaccines
        if vaccine.available_doses == 0:
            print("Not enough available doses!")

        # check 2: there must be an availability for the date
        cm = ConnectionManager()
        conn = cm.create_connection()
        cursor = conn.cursor()

        caregiver_name = None
        get_caregiver_name = "SELECT TOP 1 Username FROM Availabilities WHERE Time = %s ORDER BY Username ASC"
        try:
            cursor.execute(get_caregiver_name, date)
            # check if there is no availability for the date
            if cursor.rowcount == 0:
                print("No caregiver is available!")
                return
            for row in cursor:
                caregiver_name = row[0]
        except pymssql.Error as e:
            print("Db-Error:", e)
            print("Please try again!")
            return
        finally:
            cm.close_connection()

        # remove appointed availability
        conn = cm.create_connection()
        cursor = conn.cursor()

        remove_availability = "DELETE FROM Availabilities WHERE Username = %s AND Time = %s"
        try:
            cursor.execute(remove_availability, (caregiver_name, date))
            conn.commit()
        except pymssql.Error:
            print("Error occurred when remove availability")
            raise
        finally:
            cm.close_connection()

        # make the vaccination schedule
        conn = cm.create_connection()
        cursor = conn.cursor()

        id = random.randint(1000000, 9999999)
        add_schedule = "INSERT INTO Schedules VALUES (%d, %s, %s, %s, %s)"
        try:
            cursor.execute(add_schedule, (id, caregiver_name, self.username,
                                          vaccine.get_vaccine_name(), date))
            conn.commit()
        except pymssql.Error:
            print("Error occurred when insert schedule")
            raise
        finally:
            cm.close_connection()

        # update vaccine availability
        vaccine.decrease_available_doses(1)

        print("Appointment ID:", id, "Caregiver username:", caregiver_name)
        print("Reserved successfully.")

    # get all the vaccination schedules
    def get_schedules(self):
        cm = ConnectionManager()
        conn = cm.create_connection()
        cursor = conn.cursor()

        get_schedules = "SELECT appointment_id, Vname, Time, Cname FROM\
            Schedules WHERE Pname = %s ORDER BY appointment_id ASC"
        try:
            cursor.execute(get_schedules, self.username)
            print('%-20s' % "Appointment_ID", '%-20s' % "Vaccine", '%-20s' % "Date", '%-20s' % "Caregiver")
            if cursor.rowcount == 0:
                print("No schedules!")
            else:
                for row in cursor:
                    print('%-20s' % row[0], '%-20s' % row[1], '%-20s' % row[2], '%-20s' % row[3])
        except pymssql.Error:
            print("Error occurred when getting schedules")
            raise
        finally:
            cm.close_connection()
        return None
