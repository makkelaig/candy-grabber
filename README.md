# IoT candy-grabber
python project to remotely control a candy grabber with python-opcua via a Node-RED dashboard

This repository is part of the project: "IoT Application for a candy grabber"
for the degree mechatronics/robotics on the UAS Technikum Vienna, 2018.

### The following section is for the FHTW students that will continue to work on this project:
To run the candy grabber in the UAS Technikum LAN connect it to a router that allows access to the LAN for students. 
Power up the raspberry pi and the motor HAT, ssh into it and start the python program "candy_server.py" in the repository folder "candy-grabber" on the Desktop.

$ ssh pi@\< your Raspberry Pi IP address \><br/>
ask your supervisor for the password

$ cd Desktop/candy-grabber"<br/>
$ python3 candy_server.py<br/>

Next, create another remote connection to the pi and start the Node-RED server:

$ node-red-start<br/>

To open the Node-RED flow editor, start a browser on any device connected to the UAS Technikum LAN and enter the Raspberry Pis IP Adress followed by port 1880. To open the Node-RED dashboard add /ui to the port:

\< your Raspberry Pi IP address \>:1880/ui<br/>

If you want to change the camera settings on the RPi Web Cam Interface, 
you can do that on its interface accessible at the port specified in the bachelor paper on page 22.
To stop the opcua server type exit() in its interactive shell.
To stop Node-RED use: 

$ node-red-stop

You find all neccessary, additional information in the bachelor paper accompanying this project. 
If you run into problems don't hesitate to contact me.

## Special Thanks to all developers who contributed to this project:
https://nodered.org/<br/>
https://elinux.org/RPi-Cam-Web-Interface<br/>
https://github.com/FreeOpcUa/python-opcua<br/>
https://github.com/mikakaraila/node-red-contrib-opcua and https://github.com/biancode/node-red-contrib-iiot-opcua <br/>
https://github.com/pytransitions/transitions<br/>



