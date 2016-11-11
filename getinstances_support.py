import boto3

def get_unique_image_ids(instances):

    unique_images = set([])

    for i in instances:
        unique_images.add(i.image_id)

    return unique_images

def compile_image_data(instances, ec2_resource):

    img_set = get_unique_image_ids(instances)

    img_data_dict = {}

    for img in img_set:

        temp = ec2_resource.Image(img)
        try:
            arch = temp.architecture
            img_type = temp.image_type
            desc = temp.description
            platform = temp.platform
            tags = temp.tags
        except:
            arch = img_type = desc = platform = tags = 'invalid'

        img_data_dict[img] = {'arch':arch, 'img_type': img_type, 'desc': desc, 'platform': platform, 'tags': tags}

    return img_data_dict