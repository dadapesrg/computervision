This is one of the repositories of the Power and Energy Systems Research Group (PESRG). The Security Surveillance Research Project is foucsed on using computer vision to solve security challenges in real-time. The Computer Vision Team members are:
1. Joseph O. Dada - Group Leader
2. Ayodeji O. Salau
3. Adeayo O. Adegbesan
4. Divine Adjeroh
   
The Security Surveillance project code directory consists of the following components:
1. Templates: Which has the webpages that can be accessed through the main Python flask code
2. Data: The data set that was used for the model training with their given labels you can replace this with every dataset you have available. The sound playback file is also here
3. Video: You can store any video for testing here. The output is also stored here
4. Runs: Has the trained model alongside some performance and validation graphs
5. Config.yaml: This helps to initialise your data set classes for training
6. Credentials. Json: Hold all the information about the Firebase API
7. Main.py: This script helps you train your model from your config.yaml file
8. Read from a video.py: This script is for object detection using a stored video file in the directory
9. LiveCameraDetect.py: This script is the main code for livestream and object detection
10. PICODE.py: This is the edited version of the livecameradetect code to run on the raspberry pi
