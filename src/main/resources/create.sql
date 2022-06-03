CREATE TABLE Caregivers (
    Username varchar(255),
    Salt BINARY(16),
    Hash BINARY(16),
    PRIMARY KEY (Username)
);

CREATE TABLE Patients (
    Username varchar(255),
    Salt BINARY(16),
    Hash BINARY(16),
    PRIMARY KEY (Username)
);

CREATE TABLE Availabilities (
    Time date,
    Username varchar(255) REFERENCES Caregivers,
    PRIMARY KEY (Time, Username)
);

CREATE TABLE Vaccines (
    Name varchar(255),
    Doses int,
    PRIMARY KEY (Name)
);

CREATE TABLE Schedules (
    appointment_id int,
    Cname varchar(255) REFERENCES Caregivers(Username),
    Pname varchar(255) REFERENCES Patients(Username),
    Vname varchar(255) REFERENCES Vaccines(Name),
    Time date,
    PRIMARY KEY (appointment_id, Cname, Pname, Vname, Time)
);
