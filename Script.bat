@echo off
pip -V
pip install opencv-contrib-python
pip install opencv-python
pip install pandas
pip install numpy
pip install mysql-connector-python
pip install Pillow
echo
echo Done
timeout /t 60
