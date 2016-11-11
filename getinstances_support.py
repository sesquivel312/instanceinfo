import csv


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
    csvwriter.writerow(('instance_id', 'private_dns_name', 'private_ip', 'instance_name','instance_tags','image_id', 'architecture',
                        'image_type', 'description', 'platform', 'image_tags'))

    for instance in instances:

        # get the instance attributes we care about
        inst_id = instance.id
        priv_dns = instance.private_dns_name
        priv_ip = instance.private_ip_address
        inst_name = [dict['Value'] for dict in instance.tags if dict['Key'] == 'Name'].pop()
        inst_tags = [dict.items() for dict in instance.tags if dict['Key'] != 'Name']

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

        row = [inst_id, priv_dns, priv_ip, inst_name, inst_tags, img_id, arch, img_type, desc, platform, img_tags]

        csvwriter.writerow(row)

    f.flush()
    f.close()