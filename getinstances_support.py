def get_unique_image_ids(instances):

    unique_images = set([])

    for i in instances:
        unique_images.add(i.image_id)

    return unique_images

def compile_image_data(instances, ec2_resource):
    """
    returns a dict of dicts, top level are the image id's, with attached image attributes
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