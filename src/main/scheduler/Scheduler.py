"""
Lang Qin
HW 6 CSE 414

Note: I modified the main method and relative methods to implement the
    strong password check with at least one upper case letter, while keeping
    all the other information lowercased.
"""


from model.Vaccine import Vaccine
from model.Caregiver import Caregiver
from model.Patient import Patient
from util.Util import Util
from db.ConnectionManager import ConnectionManager
import pymssql
import datetime


'''
objects to keep track of the currently logged-in user
Note: it is always true that at most one of currentCaregiver and
        currentPatient is not null since only one user can be
        logged-in at a time
'''
current_patient = None

current_caregiver = None


def create_patient(tokens):
    # create_patient <username> <password>
    # check 1: the length for tokens need to be exactly 3 to include all
    #          information (with the operation name)
    if len(tokens) != 3:
        print("Failed to create user.")
        return

    username = tokens[1].lower()
    password = tokens[2]
    # check 2: check if the username has been taken already
    if username_exists(username):
        print("Username taken, try again!")
        return

    # check 3: check if the password is strong enough
    if not check_strong_password(password):
        print("Password is not strong enough.")
        return

    salt = Util.generate_salt()
    hash = Util.generate_hash(password, salt)

    # create the patient
    patient = Patient(username, salt=salt, hash=hash)

    # save to patient information to our database
    try:
        patient.save_to_db()
    except pymssql.Error as e:
        print("Failed to create user.")
        print("Db-Error:", e)
        quit()
    except Exception as e:
        print("Failed to create user.")
        print(e)
        return
    print("Created user ", username)


def create_caregiver(tokens):
    # create_caregiver <username> <password>
    # check 1: the length for tokens need to be exactly 3 to include all
    # information (with the operation name)
    if len(tokens) != 3:
        print("Failed to create user.")
        return

    username = tokens[1].lower()
    password = tokens[2]
    # check 2: check if the username has been taken already
    if username_exists(username, True):
        print("Username taken, try again!")
        return

    # check 3: check if the password is strong enough
    if not check_strong_password(password):
        print("Password is not strong enough.")
        return

    salt = Util.generate_salt()
    hash = Util.generate_hash(password, salt)

    # create the caregiver
    caregiver = Caregiver(username, salt=salt, hash=hash)

    # save to caregiver information to our database
    try:
        caregiver.save_to_db()
    except pymssql.Error as e:
        print("Failed to create user.")
        print("Db-Error:", e)
        quit()
    except Exception as e:
        print("Failed to create user.")
        print(e)
        return
    print("Created user ", username)


def username_exists(username, is_caregivers=False):
    # return true if the username exists in the corresponding database;
    # otherwise false.
    username = username.lower()

    cm = ConnectionManager()
    conn = cm.create_connection()

    if is_caregivers:
        select_username = "SELECT * FROM Caregivers WHERE Username = %s"
    else:
        select_username = "SELECT * FROM Patients WHERE Username = %s"

    try:
        cursor = conn.cursor(as_dict=True)
        cursor.execute(select_username, username)
        # returns false if the cursor is not before the first record or if
        # there are no rows in the ResultSet.
        for row in cursor:
            return row['Username'] is not None
    except pymssql.Error as e:
        print("Error occurred when checking username")
        print("Db-Error:", e)
        quit()
    except Exception as e:
        print("Error occurred when checking username")
        print("Error:", e)
    finally:
        cm.close_connection()
    return False


def check_strong_password(password):
    # returns true if the password is strong enough; otherwise false.
    # check 1: if the password is at least 8 characters long
    if len(password) < 8:
        print("Password must be at least 8 characters long.")
        return False

    # check 2: if the password contains both uppercase and lowercase letters
    if not any(c.islower() for c in password):
        print("Password must contain at least one lowercase letter.")
        return False
    if not any(c.isupper() for c in password):
        print("Password must contain at least one uppercase letter.")
        return False

    # check 3: if the password contains both letters and numbers
    if not any(c.isdigit() for c in password):
        print("Password must contain at least one number.")
        return False
    if not any(c.isalpha() for c in password):
        print("Password must contain at least one letter.")
        return False

    # check 4: if the password contains at least one special character
    if not any(c in '!@#?' for c in password):
        print("Password must contain at least one special character,")
        print("such as !, @, #, or ?")
        return False

    return True


def login_patient(tokens):
    # login_patient <username> <password>
    # check 1: if someone's already logged-in, they need to log out first
    global current_patient
    if current_patient is not None or current_caregiver is not None:
        print("User already logged in.")
        return

    # check 2: the length for tokens need to be exactly 3 to include all
    # information (with the operation name)
    if len(tokens) != 3:
        print("Login failed.")
        return

    username = tokens[1].lower()
    password = tokens[2]

    patient = None
    try:
        patient = Patient(username, password=password).get()
    except pymssql.Error as e:
        print("Login failed.")
        print("Db-Error:", e)
        quit()
    except Exception as e:
        print("Login failed.")
        print("Error:", e)
        return

    # check if the login was successful
    if patient is None:
        print("Login failed.")
    else:
        print("Logged in as: " + username)
        current_patient = patient


def login_caregiver(tokens):
    # login_caregiver <username> <password>
    # check 1: if someone's already logged-in, they need to log out first
    global current_caregiver
    if current_caregiver is not None or current_patient is not None:
        print("User already logged in.")
        return

    # check 2: the length for tokens need to be exactly 3 to include all
    # information (with the operation name)
    if len(tokens) != 3:
        print("Login failed.")
        return

    username = tokens[1].lower()
    password = tokens[2]

    caregiver = None
    try:
        caregiver = Caregiver(username, password=password).get()
    except pymssql.Error as e:
        print("Login failed.")
        print("Db-Error:", e)
        quit()
    except Exception as e:
        print("Login failed.")
        print("Error:", e)
        return

    # check if the login was successful
    if caregiver is None:
        print("Login failed.")
    else:
        print("Logged in as: " + username)
        current_caregiver = caregiver


def search_caregiver_schedule(tokens):
    # search_caregiver_schedule <date>
    # check 1: if someone's not logged-in, they need to log in first
    if current_caregiver is None and current_patient is None:
        print("Pleasee log in first.")
        return

    # check 2: the length for tokens need to be exactly 2 to include all
    # information (with the operation name)
    if len(tokens) != 2:
        print("Please try again!")
        return

    date = tokens[1].lower()
    # assume input is hyphenated in the format mm-dd-yyyy
    date_tokens = date.split("-")
    month = int(date_tokens[0])
    day = int(date_tokens[1])
    year = int(date_tokens[2])

    # check 3: the date must be valid
    try:
        d = datetime.date(year, month, day)
    except ValueError:
        print("Invalid date. Please try again!")
        return

    # obtain current user
    if current_patient is not None:
        user = current_patient
    else:
        user = current_caregiver

    # obtain the caregivers that are available for the date
    print("Available caregivers:")
    try:
        user.get_caregiver_availability(d)
    except pymssql.Error as e:
        print("Search caregiver availabilies failed.")
        print("Db-Error:", e)
        quit()
    except Exception as e:
        print("Error occurred when searching caregiver availabilities")
        print("Error:", e)
        return

    # obtain the number of available doses left for each vaccine
    print()
    print("Available vaccines:")
    try:
        user.get_vaccine_availability()
    except pymssql.Error as e:
        print("Search vaccine availabilies failed.")
        print("Db-Error:", e)
        quit()
    except Exception as e:
        print("Error occurred when searching vaccine availabilities")
        print("Error:", e)
        return


def reserve(tokens):
    # reserve <date> <vaccine>
    # check 1: check if the current logged-in user is a patient
    if current_patient is None and current_caregiver is None:
        print("Please login first!")
        return

    if current_patient is None:
        print("Please login as a patient first!")
        return

    # check 2: the length for tokens need to be exactly 3 to include all
    # information (with the operation name)
    if len(tokens) != 3:
        print("Please try again!")
        return

    date = tokens[1].lower()
    vaccine_name = tokens[2].lower()
    # assume input is hyphenated in the format mm-dd-yyyy
    date_tokens = date.split("-")
    month = int(date_tokens[0])
    day = int(date_tokens[1])
    year = int(date_tokens[2])

    # check 3: the date must be valid
    try:
        d = datetime.date(year, month, day)
    except ValueError:
        print("Invalid date. Please try again!")
        return

    # check 4: the vaccine must exist
    vaccine = None
    try:
        vaccine = Vaccine(vaccine_name, 0).get()
    except pymssql.Error as e:
        print("Db-Error:", e)
        quit()
    except Exception as e:
        print("Error occurred when checking vaccine availability")
        print("Error:", e)
        return

    if vaccine is None:
        print("No such vaccine. Please try again!")
        return

    # reserve the vaccine
    current_patient.make_schedule(vaccine, d)


def upload_availability(tokens):
    #  upload_availability <date>
    #  check 1: check if the current logged-in user is a caregiver
    global current_caregiver
    if current_caregiver is None:
        print("Please login as a caregiver first!")
        return

    #  check 2: the length for tokens need to be exactly 2 to include all
    #  information (with the operation name)
    if len(tokens) != 2:
        print("Please try again!")
        return

    date = tokens[1].lower()
    #  assume input is hyphenated in the format mm-dd-yyyy
    date_tokens = date.split("-")
    month = int(date_tokens[0])
    day = int(date_tokens[1])
    year = int(date_tokens[2])
    try:
        d = datetime.datetime(year, month, day)
        current_caregiver.upload_availability(d)
    except pymssql.Error as e:
        print("Upload Availability Failed")
        print("Db-Error:", e)
        quit()
    except ValueError:
        print("Please enter a valid date!")
        return
    except Exception as e:
        print("Error occurred when uploading availability")
        print("Error:", e)
        return
    print("Availability uploaded!")


def cancel(tokens):
    """
    TODO: Extra Credit
    """
    pass


def add_doses(tokens):
    #  add_doses <vaccine> <number>
    #  check 1: check if the current logged-in user is a caregiver
    global current_caregiver
    if current_caregiver is None:
        print("Please login as a caregiver first!")
        return

    #  check 2: the length for tokens need to be exactly 3 to include all
    #  information (with the operation name)
    if len(tokens) != 3:
        print("Please try again!")
        return

    vaccine_name = tokens[1].lower()
    doses = int(tokens[2])
    vaccine = None
    try:
        vaccine = Vaccine(vaccine_name, doses).get()
    except pymssql.Error as e:
        print("Error occurred when adding doses")
        print("Db-Error:", e)
        quit()
    except Exception as e:
        print("Error occurred when adding doses")
        print("Error:", e)
        return

    # if the vaccine is not found in the database, add a new (vaccine, doses)
    # entry. else, update the existing entry by adding the new doses
    if vaccine is None:
        vaccine = Vaccine(vaccine_name, doses)
        try:
            vaccine.save_to_db()
        except pymssql.Error as e:
            print("Error occurred when adding doses")
            print("Db-Error:", e)
            quit()
        except Exception as e:
            print("Error occurred when adding doses")
            print("Error:", e)
            return
    else:
        # if the vaccine is not null, meaning that the vaccine already exists
        # in our table
        try:
            vaccine.increase_available_doses(doses)
        except pymssql.Error as e:
            print("Error occurred when adding doses")
            print("Db-Error:", e)
            quit()
        except Exception as e:
            print("Error occurred when adding doses")
            print("Error:", e)
            return
    print("Doses updated!")


def show_appointments(tokens):
    # check 1: if someone's not logged-in, they need to log in first
    if current_caregiver is None and current_patient is None:
        print("Pleasee log in first.")
        return

    if current_patient is not None:
        user = current_patient
    else:
        user = current_caregiver

    # show appointments
    try:
        user.get_schedules()
    except Exception as e:
        print("Error:", e)
        print("Please try again!")
        return


def logout(tokens):
    global current_patient, current_caregiver
    # check 1: if someone's not logged-in, they need to log in first
    if current_caregiver is None and current_patient is None:
        print("Pleasee log in first.")
        return

    # logout
    try:
        if current_patient is not None:
            current_patient = None
        if current_caregiver is not None:
            current_caregiver = None
    except Exception as e:
        print("Error:", e)
        print("Please try again!")
        return

    print("Successfully logged out!")


def start():
    stop = False
    print()
    print(" *** Please enter one of the following commands *** ")
    print("> create_patient <username> <password>")
    print("> create_caregiver <username> <password>")
    print("> login_patient <username> <password>")
    print("> login_caregiver <username> <password>")
    print("> search_caregiver_schedule <date>")
    print("> reserve <date> <vaccine>")
    print("> upload_availability <date>")
    print("> cancel <appointment_id>")
    print("> add_doses <vaccine> <number>")
    print("> show_appointments")
    print("> logout")
    print("> Quit")
    print()
    print("Notice: Please use a strong password for all users.")
    print("    - must be at least 8 characters long.")
    print("    - must be a mixture of both uppercase and lowercase letters.")
    print("    - must be a mixture of letters and numbers.")
    print("    - must include of at least one special character, from “!”, “@”, “#”, “?”.")
    print()
    while not stop:
        response = ""
        print("> ", end='')

        try:
            response = str(input())
        except ValueError:
            print("Please try again!")
            break

        # response = response.lower()
        tokens = response.split(" ")
        if len(tokens) == 0:
            ValueError("Please try again!")
            continue
        operation = tokens[0].lower()
        if operation == "create_patient":
            create_patient(tokens)
        elif operation == "create_caregiver":
            create_caregiver(tokens)
        elif operation == "login_patient":
            login_patient(tokens)
        elif operation == "login_caregiver":
            login_caregiver(tokens)
        elif operation == "search_caregiver_schedule":
            search_caregiver_schedule(tokens)
        elif operation == "reserve":
            reserve(tokens)
        elif operation == "upload_availability":
            upload_availability(tokens)
        elif operation == cancel:
            cancel(tokens)
        elif operation == "add_doses":
            add_doses(tokens)
        elif operation == "show_appointments":
            show_appointments(tokens)
        elif operation == "logout":
            logout(tokens)
        elif operation == "quit":
            print("Bye!")
            stop = True
        else:
            print("Invalid operation name!")


if __name__ == "__main__":
    '''
    // pre-define the three types of authorized vaccines
    // note: it's a poor practice to hard-code these values, but we will do
    // this for the simplicity of this assignment
    // and then construct a map of vaccineName -> vaccineObject
    '''

    # start command line
    print()
    print("Welcome to the COVID-19 Vaccine Reservation Scheduling Application!")

    start()
