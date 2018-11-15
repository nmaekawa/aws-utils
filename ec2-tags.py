import boto3
import json
import re

# prompt for confirmation?
is_interactive = True

# replace tag, if already exists?
replace_tag = False

# define the connection region
ec2 = boto3.resource('ec2', region_name='us-west-2')

found_tags = {}

def get_ec2_and_volume_tags(ec2_base):
    global found_tags

    for instance in ec2_base:
        for t in instance.tags:
            add_tag(t, found_tags)

        for vol in instance.volumes.all():
            if vol.tags:
                for t in vol.tags:
                    add_tag(t, found_tags)

    # clean duplicated
    for k in found_tags:
        tagset = set(found_tags[k])
        found_tags[k] = list(tagset)

    print(json.dumps(found_tags, indent=4, sort_keys=True))


def add_tag(tag, tags):

    if tag['Key'] in found_tags:
        found_tags[tag['Key']].append(tag['Value'])
    else:
        found_tags[tag['Key']] = [ tag['Value'] ]


def copy_tags2vol(ec2_base, tags2copy):

    for instance in ec2_base:
        for t in instance.tags:
            if t['Key'] in tags2copy:
                for vol in instance.volumes.all():
                    add_tag2vol(t, vol, replace=replace_tag)


def add_tag2vol(tag, volume, replace=False):
    # check if tag already defined for volume
    tag_exist = False
    if volume.tags:
        for t in volume.tags:
            if t['Key'] == tag['Key']:
                print(f'volume({volume.volume_id}) already has tag({t["Key"]}) with value({t["Value"]})')
                tag_exist = True
                break

    if (not tag_exist) or (tag_exist and replace):
        print(f'copy tag({tag["Key"]}) with value({tag["Value"]})')
        volume.create_tags(Tags=[tag])
    else:
        print(f'KEEP ORIGINAL VOLUME({volume.volume_id}) tag({t["Key"]}) with value({t["Value"]})')


def add_tag2image(images_base):

    for image in images_base:
        print(f'image name is {image.name}')
        tag = image.create_tags(
            Tags=[{
                'Key': 'Name',
                'Value': f'{image.name}'}
            ]
        )
        print(f'created tag({tag}) for image({image.image_id})')


def has_tag_key(resource, key):
    if resource.tags:
        for t in resource.tags:
            if t['Key'] == key:
                return True
    return False

def tag_ami_snapshot(ami_base):
    for ami in ami_base:
        for dev in ami.block_device_mappings:
            if 'Ebs' in dev:
                snapId = dev['Ebs']['SnapshotId']
                print(f'{dev["DeviceName"]} - snap({snapId})')
                snap = ec2.Snapshot(snapId)
                print(f'snap desc: {snap.description}')
                print(f'snap CREATE TAG: ami_name = {ami.name}')
                snap.create_tags(
                    Tags=[{
                        'Key': 'ami_name',
                        'Value': ami.name}
                    ]
                )
                if snap.tags:
                    for t in snap.tags:
                        print(f'Tag {t["Key"]}:{t["Value"]}')

def tag_snapshots():
    snap_base = ec2.snapshots.filter(OwnerIds=['self'])
    print(f'FOUND {len(list(snap_base))} snapshots!')

    for snap in snap_base:
        #print(f'snap({snap.snapshot_id}): {snap.description}')
        has_name = False
        if snap.tags:
            tagList = [t['Key'] for t in snap.tags]
            if 'Name' not in tagList:
                has_name = True
                if snap.description.startswith('Created by CreateImage'):
                    m = re.search(
                        '(vol-[a-f0-9]+)',
                        snap.description)
                    volume_id = m[0]
                    volume = ec2.Volume(volume_id)
                    print(f'associated with volume {volume_id}')
                    try:
                        volume_state = volume.state
                    except Error as e:
                        if 'InvalidVolume.NotFound' in e:
                            print(f'volume({volume_id}) does not exist')
                            pass
                        if volume.attachments:
                            for a in volume.attachments:
                                ec2_id = a['InstanceId']
                                print(f'volume attached to instance_id({ec2_id})')
                                instance = ec2.Instance(ec2_id)
                                if instance and instance.tags:
                                    for i_tag in instance.tags:
                                        if i_tag['Key'] == 'Name':
                                            print(f'volume attached to instance({i_tag["Value"]})')
                    else:
                        print(f'volume({volume_id}) NOT FOUND')



        # snapshot does not have tag `Name`


if __name__ == '__main__':
    # get all ec2 instances
    #ec2_base = ec2.instances.all()
    #print(f'FOUND {len(list(ec2_base))} instances!')

    # get images owned by us
    images_base = ec2.images.filter(Owners=['self'])
    print(f'FOUND {len(list(images_base))} images!')

    #get_ec2_and_volume_tags(ec2_base)
    #copy_tags2vol(ec2_base, ['project', 'cluster'])

    add_tag2image(images_base)
    #tag_ami_snapshot(images_base)

    #tag_snapshots()








