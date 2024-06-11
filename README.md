This is a repository by Power and Energy Systems Research Group with the following members:
1. Joseph O. Dada - Group Leader
2. Ayodeji O. Salau
3. Adeayo O. Adegbesan
   
Computer vision is one of the focused research areas of the PESRG.
The Security Surveillance project is foucsed on using computer vision to solve security challenges in real-time. The project code directory consists of the following components
−	Templates: Which has the webpages that can be accessed through the main Python flask code
−	Data: The data set that was used for the model training with their given labels you can replace this with every dataset you have available. The sound playback file is also here
−	Video: You can store any video for testing here. The output is also stored here
−	Runs: Has the trained model alongside some performance and validation graphs
−	Config.yaml: This helps to initialise your data set classes for training
−	Credentials. Json: Hold all the information about the Firebase API
−	Main.py: This script helps you train your model from your config.yaml file
−	Read from a video.py: This script is for object detection using a stored video file in the directory
−	LiveCameraDetect.py: This script is the main code for livestream and object detection
−	PICODE.py: This is the edited version of the livecameradetect code to run on the raspberry pi
