# Creates one or more SNS subscription and cloudwatch billing alarm in US Dollars for the specified account
# When the account reaches/exceeds that threshold the email address specified will be alerted 

import boto3
import re
import botocore.exceptions

def prompt_for_input(prompt_message):
    return input(prompt_message)

def validate_email(email_address):
    if re.match(r"[^@]+@[^@]+\.[^@]+", email_address):
        return True
    return False

def validate_integer_input(input_value):
    try:
        int_value = int(input_value)
        return int_value
    except ValueError:
        return None
# Tries for the profile specified and if the profile is not found then it will return an error. 
try: 
    my_profile = prompt_for_input("Please input the profile name you will use stored in ~\.aws\config: \n")
    sess = boto3.Session(profile_name=my_profile, region_name="us-east-1")
except botocore.exceptions.ProfileNotFound as e:
    print("Error: The specified profile was not found in the AWS configuration file.")
    print("Error Message:", e)
    exit()

# Boto3 Session "The Session must be in us-east-1 as this is where billing alarms are handled"
sess = boto3.Session(profile_name=my_profile, region_name="us-east-1")


# Create the session and client for SNS & Cloudwatch 
sns_client = sess.client("sns")
cw = sess.client("cloudwatch")

# Prompt for a SNS Topic name with no spaces but underscores 
sns_name = prompt_for_input("Enter SNS Topic name with no spaces, you can use underscores: \n")

# Check if topic with the same name already exists
existing_topic = None
topics = sns_client.list_topics()
for topic in topics["Topics"]:
    if topic["TopicArn"].endswith(sns_name):
        existing_topic = topic["TopicArn"]
        break

# Use existing topic or create a new one, this will help with not creating too many topics with the same name, if it already exists re-use it and avoid bloating the sns topic area:
if existing_topic:
    print(f"Using existing topic with ARN: {existing_topic}")
    topic_arn = existing_topic
else:
    try:
        result = sns_client.create_topic(Name=sns_name)
        topic_arn = result["TopicArn"]
        print("Topic created..")
    except Exception as e:
        print(f"Error creating SNS topic: {e}")
        exit()

# Prompt for an Email address for the SNS Subscription 
subscribe_endpoint = prompt_for_input("Enter an email address for the subscription: \n")

# Validate email address
if not validate_email(subscribe_endpoint):
    print("Invalid email address")
    exit()

print("Subscription created, check your emails and confirm the subscription.")

# Creates Subscription & Sets up email protocol for that particular topic, amend Topic Arn from previous SNS topic and change endpoint to respective email address.
try:
    sns_client.subscribe(
        TopicArn=topic_arn,  # Grab ARN from list_topics API call.
        Protocol="email",
        Endpoint=subscribe_endpoint,  # Input email address here
        ReturnSubscriptionArn=True,
    )
except Exception as e:
    print("Error: Unable to create the subscription.")
    print("Error Message:", e)
    exit()

# Gather information based on the alarm below 

alarm_name = input("Enter an alarm name: \n")
alarm_desc = input("Enter an alarm description: \n")
alarm_threshold = int(input("Enter the alarm threshold in integer values: \n"))
if str(alarm_threshold).isdigit() == False:
    print("Please enter integer values only")
    exit()
linked_account_id = input(
    "Please type the account ID in reference to your billing alarm, please note it can take 24hrs for this to appear if recently migrated: \n"
)

# Ask if creating multiple alarms or not
create_multiple = input("Would you like to create multiple alarms (yes/no)? \n").lower()

# Below creates the alarm, change Name, Description, Threshold and LinkedAccount & Label
def create_alarm(alarm_name, alarm_desc, alarm_threshold, linked_account_id):
    cw.put_metric_alarm(
        AlarmName=alarm_name,
        ActionsEnabled=True,
        MetricName="EstimatedCharges",
        Namespace="AWS/Billing",
        Statistic="Maximum",
        Dimensions=[
            {"Name": "Currency", "Value": "USD"},
            {"Name": "LinkedAccount", "Value": linked_account_id},
        ],
        Period=21600,
        AlarmDescription=alarm_desc,
        AlarmActions=[topic_arn],
        EvaluationPeriods=1,
        DatapointsToAlarm=1,
        Threshold=alarm_threshold,
        ComparisonOperator="GreaterThanOrEqualToThreshold",
        TreatMissingData="missing",
    )
    print(
        f"Alarm: {alarm_name} has been created, actioning on topic {topic_arn}. The threshold is {alarm_threshold} to linked account {linked_account_id}, an Email will be sent to {subscribe_endpoint} if this threshold is breached/exceeded."
    )

# If creating multiple alarms, ask how many times to loop then loop through this x amount of times according to user input
if create_multiple == "yes":
    num_of_alarms = int(input("How many alarms would you like to create? \n"))
    for i in range(num_of_alarms):
        alarm_name = input("Enter an alarm name: \n")
        alarm_desc = input("Enter an alarm description: \n")
        alarm_threshold = int(input("Enter the alarm threshold in integer values: \n"))
        linked_account_id = input("Please type the account ID in reference to your billing alarm: \n")
        create_alarm(alarm_name, alarm_desc, alarm_threshold, linked_account_id)

# If creating only one alarm, create singular alarm 
else:
    create_alarm(alarm_name, alarm_desc, alarm_threshold, linked_account_id)


