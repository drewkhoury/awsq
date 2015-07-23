(https://travis-ci.org/drewkhoury/awsq.svg?branch=master)

# awsq

awsq provides a way to query and filter data from `aws --output json ec2 describe-instances`. It expects aws cli is installed and configured. You can supply `--profile` just like with aws, or omit it and use the default aws profile. Remember to set your region in aws.

#### Get a list of instances
The simplist way to invoke awsq.
```
./awsq.py
```

#### Get a list of instances, using the `foo` aws profile
Making sure awsq uses the aws profile `foo`. Additional parameters can be added before or after the profile parameter.
```
./awsq.py --profile foo
./awsq.py --profile foo Name
./awsq.py Name --profile foo
```

#### Example Output from ./awsq.py
In it's simplist use case, awsq will display all instances, with all thier fields. This can be a great way to discover what fields you might want to query.

In this example we have two instances, the first has custom Tags (foo and bar), the second has no custom Tags.

```bash
VpcId                                   : vpc-xxx
Name                                    : foo
InstanceId                              : i-xxx
SubnetId                                : subnet-xxx
PublicIpAddress                         : 52.0.0.1
NetworkInterfaces.0.PrivateIpAddress    : 10.0.0.1
PrivateIpAddress                        : 10.0.0.1
foo                                     : foo-data
bar                                     : bar-data

VpcId                                   : vpc-xxx
Name                                    : foo
InstanceId                              : i-xxx
SubnetId                                : subnet-xxx
PublicIpAddress                         : 52.0.0.1
NetworkInterfaces.0.PrivateIpAddress    : 10.0.0.1
PrivateIpAddress                        : 10.0.0.1
```

#### Display fields
Get a list of Instances, showing the common field `InstanceId` and the aws custom Tag `Name`.
```
./awsq.py InstanceId Name

## example output
i-xxx :: foo-name :: 
i-xxx :: bar-name :: 
```

#### Filter (=)
Filter the list to only show instances that exactly match VpcId `vpc-xxx`.
```
./awsq.py VpcId=vpc-foo InstanceId Name

## example output
vpc-foo :: i-xxx :: foo-name :: 
vpc-foo :: i-xxx :: bar-name :: 
```

#### Filter (~)
Filter the list to only show instances that part match PrivateIpAddress of `10.0.1.`.
```
./awsq.py PrivateIpAddress~10.0.1.

# example output
10.0.1.1 :: foo-name :: 
10.0.1.2 :: bar-name :: 
```
