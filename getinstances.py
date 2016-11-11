import getinstances_support as support
import boto3
import csv
import pprint as pp

# constants and flags
# aws_profile = 'default'
aws_profile = 'ew'
aws_region = 'us-west-2'
csvfilepath = 'instanceinfo.csv'
csvheaders = ['img_id','architecture','img_type','description','platform','tags']

# create the boto3 resource, via a session.  using this method to allow boto3 profile selection
ec2_session = boto3.session.Session(profile_name=aws_profile)  # using session allows selection of aws profile
ec2_resource = ec2_session.resource('ec2', region_name=aws_region)

# prefetch all instance info
instances = ec2_resource.instances.all()

# build a dict of interesting image attributes
img_data_dict = support.compile_image_data(instances, ec2_resource)

# todo: for each instance create a CSV row of interesting information
# probably something like: instance_id, priv_dns, priv_ip, <assoc_image_info_fields>


# create a CSV to hold data
# csvfile = open(csvfilepath, 'w')
# csvwriter = csv.writer(csvfile)
# csvwriter.writerow(csvheaders)
# csvwriter.writerow((image, arch, img_type, desc, platform, tags))
#
# csvfile.flush()
# csvfile.close()

