# cloudwatch-billing-alarm

The purpose of this Python file is to run one script to create a Billing-Alarm for a particular AWS Account fast an efficiently.

This will also create an SNS Topic & Subscription to alert the newly created distribution group of any Billing Alarms that have been reached or exceeded.

# Usage

To use this you can clone the code with git or download the .py file.

You can run it in PowerShell or via WSL/CLI:

PS Example:

```
cd C:\Projects\

create-cw-alarm-simple.py

```

WSL/CLI Example:

```
cd Projects/cloudwatch-billing-alarm

Python3 create-cw-alarm-simple.py
```

# NOTE

You must have AWS CLI installed and have an AWS Profile configured in ~\.aws\config

You will also have to log in to AWS CLI before runninng the script, see further information below:

# If AWS CLI is not configured already

```
aws configure --profile
```

# Login to AWS CLI

```
aws sso login --profile your-aws-sso-profile
```

# Full Example Below

```
~$ aws sso login --profile sso-profile-here

Attempting to automatically open the SSO authorization page in your default browser.
If the browser does not open or you wish to use a different device to authorize this request, open the following URL:

https://device.sso.eu-west-1.amazonaws.com/

Then enter the code: *****


Successfully logged into Start URL: https://aags.awsapps.com/start
```

```
~$ /bin/python3 /home/user/Projects/cloudwatch-billing-alarm/create-cw-alarm-simple.py
Please input the profile name you will use stored in ~\.aws\config: 
sso-profile-name-here

Enter SNS Topic name with no spaces, you can use underscores: 
Test_Topic_Delete_Me


Topic Created..

Enter an email address for the subscription: 

mymail@email.com

Subscription created, check your emails and confirm the subscription.

Enter an alarm name: 

Test_Alarm_Delete_Me

Enter an alarm description: 

delete

Enter the alarm threshold in integer values: 

500


Please type the account ID in reference to your billing alarm, please note it can take 24hrs for this to appear if recently migrated: 

677192264473


Alarm: Test_Alarm_Delete_Me has been created, actioning on topic arn:aws:sns:us-east-1:847159393223:Test_Topic_Delete_Me. The threshold is 500 to linked account 677192264473, an Email will be sent to mymail@email.com if this threshold is breached/exceeded.
```
