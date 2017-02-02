#!/usr/bin/env python

import boto3

import lib

cli_args = lib.get_cli_args()

# create the boto3 resource, via a session.  using this method to allow boto3 profile selection
ec2_session = boto3.session.Session(profile_name=cli_args.profile)  # using session allows selection of aws profile
ec2_resource = ec2_session.resource('ec2', region_name=cli_args.region)

# prefetch all instance info
instances = ec2_resource.instances.all()

# build a dict of interesting image attributes
img_data_dict = lib.compile_image_data(instances, ec2_resource)

#create the output csv file
lib.create_instance_csv_file(instances, img_data_dict, cli_args.output)
