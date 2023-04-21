# Parts-replacement 
Project Description
What the app does?
The Problem:
When a hardware component is detected as faulty, it requires a replacement.
The manual flow: 
-> Pull data from the servers, based on component type
-> Create JIRA ticket
-> Push all info
-> Link system and failure tickets to the replacement ticket
-> Send approval for replacement
~Average of 1 hour work per component

The Solution:
-> Manual Jenkins trigger: provide all basic info(system id, component type, component number)
-> Jenkins job runs this automation
-> Connect to the system's server
-> Pull all relevant info based on component type & number
-> Create JIRA ticket with the info from the last step + system general info
-> JIRA Links
-> JIRA resolutions(trigger replacement start)

Why I use the tochnologies I use: 
Jenkins: Initial trigger + basic info + user friendly environment
JIRA API: Connection to the JIRA domain and remote actions using Python

Future features:
Fully automatic trigger
Better logging system
Use DataClasses for better readability

## Setup

Clone the repository
```
curl https://bootstrap.pypa.io/get-pip.py | python3.7
pip install requirements.txt
```

### Local run

```
python3.7 ./main.py $SYSTEM $COMPONENT $PART_NUMBER --side $SIDE --drive-type ${DRIVE_TYPE} --rejection ${RC} --description ${DESCRIPTION} --resolution ${RESOLUTION} --no-logs $NO_LOGS --locator $LOCATOR --sfp-type $SFP_TYPE --node $NODE -u $BUILD_USER_ID -p $JIRA_PASSWORD
```

#### How to use

