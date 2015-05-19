# awsq

awsq provides a way to query and filter data from `aws --output json ec2 describe-instances`. It expects aws cli is installed and configured. You can supply `--profile` just like with aws, or omit it and use the default aws profile.

Examples:

```
# get a list of instances
./awsq.py

# get a list of instances, use the `foo` aws profile
./awsq.py --profile foo

# Example Output from ./awsq.py
# In this example we have two instances,
# The first has custom Tags (foo and bar),
# The second has no custom Tags.
#
# VpcId                                   : vpc-xxx
# Name                                    : foo
# InstanceId                              : i-xxx
# SubnetId                                : subnet-xxx
# PublicIpAddress                         : 52.0.0.1
# NetworkInterfaces.0.PrivateIpAddress    : 172.0.0.1
# PrivateIpAddress                        : 172.0.0.1
# foo                                     : foo-data
# bar                                     : bar-data
#
# VpcId                                   : vpc-xxx
# Name                                    : foo
# InstanceId                              : i-xxx
# SubnetId                                : subnet-xxx
# PublicIpAddress                         : 52.0.0.1
# NetworkInterfaces.0.PrivateIpAddress    : 172.0.0.1
# PrivateIpAddress                        : 172.0.0.1

# get a list of Instances,
# showing the regular field InstanceId
# and the aws tag foo
./awsq.py InstanceId Name

# Filter the list to only show instances that equal VpcId of `vpc-xxx`
./awsq.py VpcId=vpc-xxx InstanceId Name

# Filter the list to only show instances that part match PrivateIpAddress of `172`
./awsq.py PrivateIpAddress~172

```