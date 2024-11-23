# GooseBuster

The GooseBuster project is designed to protect a lawn from damage caused by geese.

A Raspberry Pi, connected to multiple cameras, periodically captures images of the lawn. These images are analyzed using a Roboflow-trained model to specifically detect Canada geese.

When geese are detected:

- An inflatable scarecrow (the "airdancer") is activated to scare them away.
- An email alert is sent to monitor the system's effectiveness.
  
To further deter geese:

- Animal sounds are played randomly through two speakers, preventing geese from adapting to the system.
- 
This setup offers an automated and efficient way to keep geese off the lawn.
