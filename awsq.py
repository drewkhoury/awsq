#!/usr/bin/env python
#
# Query AWS nodes and print out results
# Copyright (C) 2014 Daniel Lawrence
#
# This program is free software; you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the
# Free Software Foundation; either version 2 of the License,
# or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE.
# See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with
# this program; if not, write to the Free Software Foundation, Inc.,
# 59 Temple Place, Suite 330, Boston, MA 02111-1307 USA
#
######################
import os
import json
import collections
import sys
import pprint
import time
import hashlib

# execute a command and output to a cache file
def execute (cmd):

    cachelife = 60*60*2
    cachename = '/tmp/awsq-cache.%s.%s' % (os.getlogin(), hashlib.sha1(cmd).hexdigest())
    
    # if the cache exists
    if os.path.exists(cachename):
        cacheage = os.stat(cachename).st_mtime
        now = time.time()
        cacheexpire = cachelife-(now-cacheage)
        # if the cache hasn't expired yet, read from cache and let the user know when the cache will expire
        if cacheexpire > 1:
            sys.stderr.write("########## Cache expires in %s seconds\n\n" % int(cacheexpire))
            raw=open(cachename).read()
            return raw   
    
    # if the cache doesn't exist, fetch the data, and create a cache file for future use
    sys.stderr.write("########## fetching you some fresh data, cache will last %s seconds\n\n" % cachelife)
    raw=os.popen(cmd).read()
    f=open(cachename,'w')
    f.write(raw)
    f.close()
    os.chmod(cachename, 0600)
    return raw

# look for profile name
profile_data=''
i=0
for k in sys.argv:
    if k == '--profile':
        profile_data = ("--profile %s"%sys.argv[i+1])
        sys.argv.pop(i) # remove --profile
        sys.argv.pop(i) # remove profile-name
    i=i+1

raw = execute("aws --output json ec2 describe-instances %s"%profile_data)
ec2 = json.loads(raw)

# default keys we want to be able to view/filter
# we can manually add any keys from ec2d
B_KEYS = [
    'InstanceId',
    'PrivateIpAddress',
    'PublicIpAddress',
    'VpcId',
    'NetworkInterfaces.0.PrivateIpAddress',
    'NetworkInterfaces.1.PrivateIpAddress',
    'SubnetId'
]

DB = collections.defaultdict(dict)

for r in ec2['Reservations']:

    instance = r['Instances'][0]

    # --- example of keys for instance:
        # Monitoring
        # PublicDnsName
        # StateReason
        # State
        # EbsOptimized
        # LaunchTime
        # PrivateIpAddress
        # ProductCodes
        # VpcId
        # StateTransitionReason
        # InstanceId
        # ImageId
        # PrivateDnsName
        # KeyName
        # SecurityGroups
        # ClientToken
        # SubnetId
        # InstanceType
        # NetworkInterfaces
        # SourceDestCheck
        # Placement
        # Hypervisor
        # BlockDeviceMappings
        # Architecture
        # KernelId
        # RootDeviceName
        # VirtualizationType
        # RootDeviceType
        # Tags
        # AmiLaunchIndex

    # --- example of values for instance:
        # instance['Monitoring']             {u'State': u'disabled'}
        # instance['PublicDnsName']          none
        # print instance['State']            {u'Code': 16, u'Name': u'running'}
        # print instance['EbsOptimized']     False
        # print instance['LaunchTime']       2014-05-06T05:06:04.000Z
        # print instance['PrivateIpAddress'] 10.0.0.1
        #
        # instance['Tags'] = 
        # [{u'Key': u'foo', u'Value': u'bar'},
        #  {u'Key': u'aws:cloudformation:stack-id',
        #  {u'Key': u'aws:cloudformation:logical-id', u'Value': u'Instance'},
        #  {u'Key': u'AppName', u'Value': u'syslog'},
        #  {u'Key': u'aws:cloudformation:stack-name']

    #
    # Loop through instance and break it down into a flat structure,
    # this makes it much easier to access values within lists.
    #
    # We're taking the complex structure contained within instance,
    # and populating a dictionary (ec2d) with a flat hierarchy. 
    #
    ec2d = {}
    for key,value in instance.items():

        ### (1) SIMPLE VARS
        # --- example of unicode, bool, int:
            # print "%s has value %s %s"%(key,value,type(value))
            # KernelId has value aki-xxx <type 'unicode'>
            # EbsOptimized has value False <type 'bool'>
            # LaunchTime has value 2014-05-06T05:06:04.000Z <type 'unicode'>
            # PrivateIpAddress has value 10.239.0.1 <type 'unicode'>
            # VpcId has value vpc-xxx <type 'unicode'>
            # InstanceId has value i-xxx <type 'unicode'>
            # ImageId has value ami-xxx <type 'unicode'>
            # PrivateDnsName has value ip-10-0-0-1.ap-southeast-2.compute.internal <type 'unicode'>
            # KeyName has value xxx <type 'unicode'>
            # ClientToken has value xxx <type 'unicode'>
            # SubnetId has value subnet-xxx <type 'unicode'>
            # InstanceType has value m1.small <type 'unicode'>
            # SourceDestCheck has value False <type 'bool'>
            # Hypervisor has value xen <type 'unicode'>
            # Architecture has value x86_64 <type 'unicode'>
            # RootDeviceType has value ebs <type 'unicode'>
            # RootDeviceName has value /dev/sda1 <type 'unicode'>
            # VirtualizationType has value paravirtual <type 'unicode'>
            # AmiLaunchIndex has value 0 <type 'int'>        
        if isinstance(value,unicode) or isinstance(value,bool) or isinstance(value,int) :
            ec2d[key] = value
            continue

        ### (2) LISTS
        if isinstance(value,list):

            # --- example of i,item given enumerate(value)
                # enumerate returns the index and content,
                # our for loop will now get
                # i=0, item=apples
                # i=1, item=bannana
                #
                # print "i=%s item=%s"%(i,item)
                # i=0 item={u'GroupName': u'xxx', u'GroupId': u'sg-xxx'}
                # i=1 item={u'GroupName': u'xxx', u'GroupId': u'sg-xxx'}
            for i,item in enumerate(value):
                if isinstance(item,dict):
                    for x,y in item.items():
                        ### (2a) LEVEL 1 DEEP LISTS
                        if isinstance(y,unicode) or isinstance(y,bool):
                            ec2d["%s.%s.%s"%(key,i,x)] = y
                        ### (2b) LEVEL 2 DEEP LISTS
                        elif isinstance(y,list) : # repeat loop stuff (we should do this via a recursive loop)
                            for i2,item2 in enumerate(y):
                                if isinstance(item2,dict):
                                    for x2,y2 in item2.items():
                                        if isinstance(y2,unicode) or isinstance(y2,bool):
                                            ec2d["%s.%s.%s.%s.%s"%(key,i,x,i2,x2)] = y2
            continue
        
        ### (3) None
        if value is None:
            continue

        ### (4) Dict
        # --- example of dict:
            # print "%s has value %s %s"%(key,value,type(value))
            # Monitoring has value {u'State': u'disabled'} <type 'dict'>
            # State has value {u'Code': 16, u'Name': u'running'} <type 'dict'>
            # Placement has value {u'GroupName': None, u'Tenancy': u'default', u'AvailabilityZone': u'ap-southeast-2a'} <type 'dict'>
        if isinstance(value,dict):
            for key2,value2 in value.items():
                ec2d["%s.%s" %(key,key2)] = value2
            continue

    d = {}
    name = None

    # Only care about servers that are running.
    if ec2d['State.Name'] != 'running':
        continue

    # Print all the basic keys
    for k in B_KEYS:
        if k in ec2d:
            d[k] = ec2d[k]

    # Grab all the tags
    tags = {}
    for t in instance['Tags']:
        k = t['Key']
        v = t['Value']
        tags[k] = v
    d.update(tags)

    # Work on if we have a name for the instance.
    if 'Name' not in d:
        Name = d['InstanceId']

    # print all or some
    if len(sys.argv) == 1:
        for k, v in d.items():
            print "%-40s: %s" % (k, v)
        print
    else:
        s = ""
        SKIP = False
        for k in sys.argv[1:]:

            # Overally simple Queries
            if '=' in k:
                (k, q) = k.split('=')
                if k not in d:
                    continue
                if d[k] != q:
                    SKIP = True
                    continue

            # Overally simple Queries
            if '~' in k:
                (k, q) = k.split('~')
                if k not in d:
                    continue
                if q not in d[k]:
                    SKIP = True
                    continue

            # Format
            if k in d:
                s += "%%(%s)s :: " % k
            else:
                SKIP = True

        if SKIP:
            continue

        if not s:
            continue

        # Print all the matching values to provided keys
        print s % d
