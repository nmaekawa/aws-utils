#! /usr/bin/env python

import argparse
import boto3


# define the connection region
ec2 = boto3.resource('ec2', region_name='us-west-2')

def usage():
    print('missing comma separated list of instance_ids')
    exit(1)


def copy_tags2vol(ec2_base, tags2copy):

    for instance in ec2_base:
        for t in instance.tags:
            if t['Key'] in tags2copy:
                for vol in instance.volumes.all():
                    add_tag2vol(t, vol, replace=replace_tag)


if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument(
        'ec2_ids',
        help='comma separated list of instance_ids')
    parser.add_argument(
        'tags2copy',
        help='comma separated list of tags to be copied')

    # parse args
    args = parser.parse_args()

    instance_ids = args.ec2_ids.split(',')
    instance_tags = args.tags2copy.split(',')

    #print('list of ids is {}'.format(instance_ids))
    #print('list of tags is {}'.format(instance_tags))

    for eid in instance_ids:
        instance = ec2.Instance(eid)
        for tag in instance.tags:
            if tag['Key'] in instance_tags:
                for vol in instance.volumes.all():
                    vol.create_tags(Tags=[tag])






