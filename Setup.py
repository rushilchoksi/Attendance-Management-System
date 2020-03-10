import os
import time
from pathlib import Path

path = os.getcwd()
hostMySQL = 'localhost'
userMySQL = 'root'
passMySQL = 'root'
requiredFiles = ['Attendance','TrainingImage','TrainingImageLabel'];
for i in range(3):
    if requiredFiles[i] == os.listdir():
        pass
    else:
        try:
            os.mkdir(requiredFiles[i])
        except Exception:
            pass
Path("StudentDetails.csv").touch()
print("Setup completed.")
