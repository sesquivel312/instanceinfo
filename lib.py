import csv
import argparse


def get_cli_args():
    parser = argparse.ArgumentParser(description='Collect basic data about AWS instances and its associated image')
    parser.add_argument('-p', '--profile', help='aws config profile to use, defaults to \'\'', default='')
    parser.add_argument('-r', '--region', help='aws region to use, defaults to us-west-2', default='us-west-2')
    parser.add_argument('-o', '--output', help='relative or fully qualified path to output file, defaults to ' \
                                               'instanceinfo.csv in the current directory', default='instanceinfo.csv')
    return parser.parse_args()

def get_unique_image_ids(instances):

    unique_images = set([])

    for i in instances:
        unique_images.add(i.image_id)

    return unique_images


def compile_image_data(instances, ec2_resource):
    """
    returns a dict of dicts, top level are the image id's, with attached image attributes.

    Dict structure is: {'img_id_string1':{'img_attr11':'value11',...}, 'img_id_string2':{...}, ... }

    :param instances: aws ec2 instance iterable
    :param ec2_resource: boto3 ec2 resource object
    :return: dict-of-dicts containing image attributes
    """

    img_set = get_unique_image_ids(instances)

    img_data_dict = {}

    for img in img_set:

        temp = ec2_resource.Image(img)
        try:  # sometimes getting the attributes from the image object fails, if so, fill w/dummy values indicating that
            arch = temp.architecture
            img_type = temp.image_type
            desc = temp.description
            platform = temp.platform
            tags = temp.tags
        except:
            arch = img_type = desc = platform = tags = 'invalid'

        img_data_dict[img] = {'arch':arch, 'img_type': img_type, 'desc': desc, 'platform': platform, 'tags': tags}

    return img_data_dict


def create_instance_csv_file(instances, img_data_dict, csv_file_path):

    # todo: for each instance create a CSV row of interesting information
    # probably something like: instance_id, priv_dns, priv_ip, <assoc_image_info_fields>

    # create the CSV file at the path passed as param
    f = open(csv_file_path, 'w')
    csvwriter = csv.writer(f)

    # write the header row
    csvwriter.writerow(('instance_id', 'instance_state', 'private_dns_name', 'private_ip', 'instance_name',
                        'instance_tags','image_id', 'architecture',
                        'image_type', 'description', 'platform', 'image_tags', 'public_dns',
                        'public_ip', 'network_info'))

    for instance in instances:

        # get the instance attributes we care about
        instance_id = instance.id
        instance_state = instance.state['Name']
        priv_dns = instance.private_dns_name
        priv_ip = instance.private_ip_address
        public_dns = instance.public_dns_name
        public_ip = instance.public_ip_address
        inst_name = [dict['Value'] for dict in instance.tags if dict['Key'] == 'Name'].pop()
        inst_tags = [dict.items() for dict in instance.tags if dict['Key'] != 'Name']

        # todo parse relevant info from network_info, aggregate into a single field in the output csv

        network_info = ''

        for iface in instance.network_interfaces_attribute:
            network_info += '<{}>'.format(iface['MacAddress'])
            private_ips = iface.get('PrivateIpAddresses')
            if private_ips:
                for address in private_ips:

                    network_info += address['PrivateIpAddress']

                    if address['Primary']:
                        network_info += '(P);'
                    else:
                        network_info += ';'

                    association = address.get('Association')

                    if association:
                        network_info += '{};'.format(association['PublicIp'])


        # get the image attributes associated w/the instance, via the image_id
        if instance.image_id not in img_data_dict:  # if problem getting img attrs for img_id, set values to indicate so
            img_id = arch = img_type = desc = platform = img_tags = 'not found'
        else:  #
            img_id = instance.image_id
            img_attr = img_data_dict [img_id]
            arch = img_attr['arch']
            img_type = img_attr['img_type']
            desc = img_attr['desc']
            platform = img_attr['platform']
            img_tags = img_attr['tags']

        row = [instance_id, instance_state, priv_dns, priv_ip, inst_name, inst_tags, img_id, arch,
               img_type, desc, platform, img_tags, public_dns, public_ip, network_info]

        csvwriter.writerow(row)

    f.flush()
    f.close()