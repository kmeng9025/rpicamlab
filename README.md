Hi Daniel or Zohreh or whomever it is.
The front-end kinda sucks. It is functional, but it looks not pretty. I'm gonna work on that, but kinda low priority right now.

The ai also doesn't work. I have aorund 700 annotated images, but they are lacking in quality, so I will have to go through and review all of them. Might take a bit.

Instructions for installing:
For the old raspberry pi 4s that you were using to record, they're OS is too old, and they will have to be reflashed. Please backup all the video that you have on it before doing this. Instructions for reflashing can be found [here](https://www.raspberrypi.com/documentation/computers/getting-started.html#installing-the-operating-system).
*IMPORTANT NOTE*, for fastest flashing, using raspberry pi imager. Before you click the NEXT button and start flashing, press ctrl+shift+x to open settings. UNCHECK EVERYTHING, EXCEPT for the "Set username and password". Set your username and password. For simplicities sake, just set the username and password to the default, user=pi, password=raspberry. This way if you ever forget just search it up and you'll find it. It is important that you set up the username and password, as this will save time when you first boot it.
After downloading the latest version of the raspberry pi, you should boot it. 
Then, connect to wifi. I find that plugging into ethernet is the best way. Behind Eric's desk, there is a desktop that is plugged into ethernet. (desk where I sat last time). You should be able to unplug that and plug into the raspberry pi. Then, open chrome, and search for something, literally anything, and just keep on trying to search for something until it triggers the login page (I tend to just search "hello" and keep on reloading the page). The login page should prompt you for your username and password for UMB wifi. Follow the prompts, and after everything is done, the tab should say success. Sometimes, it just endlessly "loads", but if you look at the actual tab name and it says success, then its good.

After joining the wifi, open a terminal and run the following command: 
```
git clone https://github.com/kmeng9025/rpicamlab
```
After it finishes downloading the code, you have a decision to make.

If it is a CAMERA pi, run the following command: 
```
cd rpicamlab; chmod +x ./setUpCamera.sh; ./setUpCamera.sh
```
If it is a CENTRAL pi, run the following command: 
```
cd rpicamlab; chmod +x ./setUpCentral.sh; ./setUpCentral.sh
```

It should now be good, and it will start the script every time on its own as soon as it powers on, so you don't need to worry about starting the script :). (I never tested the autorun, since i just wrote it like 5 seconds ago and I'm in school so no raspberry pi to test it on unfortunately. however, I'll test as soon as i get home, probably around 4) i hate history
