#!/usr/bin/env python

import argparse
import boto3
import getinstances_support as support

parser = argparse.ArgumentParser(description='Collect basic data about AWS instances and its associated image')
parser.add_argument('-p', '--profile', help='aws config profile to use, defaults to \'\'', default='')
parser.add_argument('-r', '--region', help='aws region to use, defaults to us-west-2', default='us-west-2')
parser.add_argument('-o', '--output', help='relative or fully qualified path to output file, defaults to ' \
                                           'instanceinfo.csv in the current directory', default='instanceinfo.csv')
args = parser.parse_args()

# create the boto3 resource, via a session.  using this method to allow boto3 profile selection
ec2_session = boto3.session.Session(profile_name=args.profile)  # using session allows selection of aws profile
ec2_resource = ec2_session.resource('ec2', region_name=args.region)

# prefetch all instance info
instances = ec2_resource.instances.all()

# build a dict of interesting image attributes
img_data_dict = support.compile_image_data(instances, ec2_resource)

support.create_instance_csv_file(instances, img_data_dict, args.output)
