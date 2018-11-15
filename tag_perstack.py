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
        'stackname',
        help='name of stack to tag')
    parser.add_argument(
        '-t', '--tags',
        required=False,
        default='project,cluster,service',
        help='comma separated list of tags to be copied')

    # parse args
    args = parser.parse_args()
    stack = args.stackname
    instance_tags = args.tags.split(',')

    #print('stack name is {}'.format(args.stackname))
    #print('list of tags is {}'.format(instance_tags))
    #exit()

    filters = [{'Name': 'tag-key', 'Values':['aws:cloudformation:stack-id']}]
    instances = ec2.instances.filter(Filters=filters)
    stack_instances = []
    print('instances {}'.format(type(instances)))
    for i in instances:
        for tag in i.tags:
            if tag['Key'] == 'aws:cloudformation:stack-id':
                if stack in tag['Value']:
                    stack_instances.append(i)

    for instance in stack_instances:
        # adding stack name because nested cf-stacks get their own stack-name
        tags = [{'Key': 'stack', 'Value': stack}]
        instance.create_tags(Tags=tags)

        for tag in instance.tags:
            if tag['Key'] in instance_tags:
                tags.append(tag)

        for vol in instance.volumes.all():
            vol.create_tags(Tags=tags)






