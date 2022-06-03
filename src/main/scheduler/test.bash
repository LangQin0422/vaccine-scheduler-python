#!/bin/bash

# define caregivers and patients
declare -a caregivers=("hallhealth" "kelley" "rose" "smith" "wilson" "young" "zhao" "zhang") 
declare -a patients=("langqin" "olivia" "sarah" "tina" "zoe" "john")

# define vaccines
declare -a vaccines=("pfizer" "moderna" "jj" "sinovac")

python Scheduler.py

# create caregivers
for caregiver in "${caregivers[@]}"
do
  create_caregiver $caregiver !A1234567890a
done

# create patients
for patient in "${patients[@]}"
do
  create_patient $patient Ql110119!
done

# create vaccines
login_caregiver hallhealth !A1234567890a
for vaccine in "${vaccines[@]}"
do
  add_doses $vaccine 1000
done
logout

# upload availability
declare -a dates=("02-22-2022" "04-22-2022" "03-22-2022" "05-22-2022" "06-22-2022" "07-22-2022")
for caregiver in "${caregivers[@]}"
do
  login_caregiver $caregiver !A1234567890a
  for date in "${dates[@]}"
  do
    upload_availability $date
  done
  logout
done


# test 1
login_patient langqin Ql110119!
search_caregiver_schedule 04-22-2022
reserve 04-22-2022 pfizer
show_appointments
logout

login_caregiver hallhealth !A1234567890a
show_appointments
logout

# test 2
login_patient olivia Ql110119!
search_caregiver_schedule 04-22-2022
reserve 04-22-2022 moderna
show_appointments
search_caregiver_schedule 02-22-2022
reserve 02-22-2022 sinovac
show_appointments
reserve 01-22-2022 pfizer
logout

login_caregiver kelley !A1234567890a
show_appointments
logout
login_caregiver hallhealth !A1234567890a
show_appointments
logout
login_caregiver smith !A1234567890a
show_appointments
logout
login_caregiver wilson !A1234567890a
add_doses pfizer 100
add_doses moderna 100
search_caregiver_schedule 04-22-2022
logout


