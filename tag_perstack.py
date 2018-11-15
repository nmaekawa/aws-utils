#! /usr/bin/env python

import argparse
import boto3


# define the connection region
ec2 = boto3.resource('ec2', region_name='us-west-2')


def valid_stack_name(stack_name):
    """minimal check for hx stack-name pattern.
    
    needed because we filter per PATTERN and if you give a stack_name
    like 'devo', all devo stack tags will be overwritten!

    the pattern for hx stack-names is <project>-<cluster>-<some_uniq_id>,
    so counting the number of '-' dashes in stack-name.
    """
    if stack_name.count('-') >= 2 and not stack_name.endswith('-'):
        return True
    else:
        return False

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
    parser.add_argument(
        '--quiet',
        action='store_true',
        help='does not print any info')

    # parse args
    args = parser.parse_args()
    instance_tags = args.tags.split(',')
    stack = args.stackname.strip()
    if not valid_stack_name(stack):
        if not args.quiet:
            print('invalid stack name({})'.format(args.stackname))
        exit(1)

    filters = [{'Name': 'tag-key', 'Values':['aws:cloudformation:stack-name']}]
    instances = ec2.instances.filter(Filters=filters)
    stack_instances = []
    stack_names = []
    for i in instances:
        for tag in i.tags:
            if tag['Key'] == 'aws:cloudformation:stack-name':
                if tag['Value'].startswith(stack):
                    stack_instances.append(i)
                    stack_names.append(tag['Value'])

    if not args.quiet:
        if not stack_instances:
            print('no instances found for stack name ({})'.format(stack))
            exit()
        else:
            print('found instances in stack(s): {}'.format(set(stack_names)))

    for instance in stack_instances:
        # adding stack name because nested cf-stacks get their own stack-name
        tags = [{'Key': 'stack', 'Value': stack}]
        instance.create_tags(Tags=tags)

        for tag in instance.tags:
            if tag['Key'] in instance_tags:
                tags.append(tag)

        for vol in instance.volumes.all():
            vol.create_tags(Tags=tags)






