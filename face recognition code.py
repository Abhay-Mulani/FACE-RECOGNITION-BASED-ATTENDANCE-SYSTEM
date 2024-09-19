import face_recognition
import cv2
import numpy as np
import os
import xlwt
from xlwt import Workbook
from datetime import date
import xlrd, xlwt
from xlutils.copy import copy as xl_copy
import time

CurrentFolder = os.getcwd() #Read current folder path
image = CurrentFolder+'\\Abhay_Mulani.jpg'

# Get a reference to webcam #0 (the default one)
video_capture = cv2.VideoCapture(0)

# Load a sample picture and learn how to recognize it.
person1_name = "Abhay_Mulani"
person1_image = face_recognition.load_image_file(image)
person1_face_encoding = face_recognition.face_encodings(person1_image)[0]

# Create arrays of known face encodings and their names
known_face_encodings = [person1_face_encoding]
known_face_names = [person1_name]

# Initialize some variables
face_locations = []
face_encodings = []
face_names = []
process_this_frame = True

rb = xlrd.open_workbook('attendence_excel.xls', formatting_info=True)
wb = xl_copy(rb)
inp = input('Please give current subject lecture name')
sheet1 = wb.add_sheet(inp)
sheet1.write(0, 0, 'Name/Date')
sheet1.write(0, 1, str(date.today()))
row=1
col=0
already_attendence_taken = ""
last_marked_time = 0
marking_cooldown = 10  # Cooldown time in seconds

while True:
    # Grab a single frame of video
    ret, frame = video_capture.read()

    # Resize frame of video to 1/4 size for faster face recognition processing
    small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)

    # Convert the image from BGR color (which OpenCV uses) to RGB color (which face_recognition uses)
    rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)

    # Only process every other frame of video to save time
    if process_this_frame:
        # Find all the faces and face encodings in the current frame of video
        face_locations = face_recognition.face_locations(rgb_small_frame)
        face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

        face_names = []
        for face_encoding in face_encodings:
            # See if the face is a match for the known face(s)
            matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
            name = "Unknown"

            # Or instead, use the known face with the smallest distance to the new face
            face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)
            best_match_index = np.argmin(face_distances)
            if matches[best_match_index]:
                name = known_face_names[best_match_index]

            face_names.append(name)
            current_time = time.time()
            if ((already_attendence_taken != name) and (name != "Unknown") and (current_time - last_marked_time > marking_cooldown)):
                sheet1.write(row, col, name )
                col =col+1
                sheet1.write(row, col, "Present" )
                row = row+1
                col = 0
                print("attendence taken")
                wb.save('attendence_excel.xls')
                already_attendence_taken = name
                last_marked_time = current_time
            else:
                print("next student")
                break

    process_this_frame = not process_this_frame
    # Display the result
    for (top, right, bottom, left), name in zip(face_locations, face_names):
        # Scale back up face locations since the frame we detected in was scaled to 1/4 size
        top *= 4
        right *= 4
        bottom *= 4
        left *= 4

        # Draw a box around the face
        cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)

        # Draw a label with a name below the face
        cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (0, 0, 255), cv2.FILLED)
        font = cv2.FONT_HERSHEY_DUPLEX
        cv2.putText(frame, name, (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)

    # Display the resulting image
    cv2.imshow('Video', frame)

    # Hit 'q' on the keyboard to quit!
    if cv2.waitKey(1) & 0xff == ord('q'):
        print("data save")
        break

# Release handle to the webcam
video_capture.release()
cv2.destroyAllWindows()

