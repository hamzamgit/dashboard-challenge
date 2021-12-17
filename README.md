## RPA CHALLENGE
This repository contains the solution of RPA Challenge for scraping [Itdashboard.org](https://itdashboard.gov/). 

## Setup (robocorp)
1. Create account on [robocorp.com](https://robocorp.com/)
2. Create a robot with public git repository and add link of this repository to it.
3. Create a process in workforce and select the robot that we created earlier.
4. Run the process for result.

### challenge.py 
- contains Class Process which has all the code of robot to complete the process

### task.py
- main script which will execute when process is triggered.

### config.py
- configuration file.

### conda.yaml
- conda environment configuration for robot environment which will be created to run the robot.

### robot.yaml
- robot configuration in which python script is configured which has be executed.
