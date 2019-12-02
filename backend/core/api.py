import logging
from uuid import uuid4

import boto3
from botocore.exceptions import ClientError
from rest_framework.status import HTTP_500_INTERNAL_SERVER_ERROR

from core.exceptions import OperationError
from ec2.constants import WORDPRESS_AMI, SECURITY_GROUP_NAME, SECURITY_GROUP_DESCRIPTION

logger = logging.getLogger(__name__)


class AmazonAPIWrapper(object):

    def __init__(self, client_id, client_secret, resource='ec2'):
        self.__client_id = client_id
        self.__client_secret = client_secret
        self.__resource = resource

        self.__get_client_resource()

    def __get_client_resource(self):
        """
        Assigns the ec2 resource object to self.client to later be used as client between the backend and AWS
        """
        try:
            self.client = boto3.resource(self.__resource,
                                         aws_access_key_id=self.__client_id,
                                         aws_secret_access_key=self.__client_secret,
                                         region_name='eu-west-1')

        except ClientError:
            raise

    def get_raw_client(self, resource='ec2'):
        return boto3.client(resource, aws_access_key_id=self.__client_id,
                            aws_secret_access_key=self.__client_secret,
                            region_name='eu-west-1')

    def security_group_exists(self, group_name=SECURITY_GROUP_NAME):
        """
        Checks if the given group name exists for the current user
        :param group_name: Name of the group
        :return: True if the group exists
        """
        security_groups = self.get_raw_client().describe_security_groups(Filters=[{
            'Name': 'group-name',
            'Values': [group_name]
        }])
        return len(security_groups['SecurityGroups']) > 0

    def get_instance(self, instance_id):
        """
        Given a instance id retrieves the instance object from AWS.
        :param instance_id: to be searched
        :return: instance
        """
        try:
            instance = self.client.Instance(instance_id)
        except Exception:
            raise OperationError('Error accessing to instance data', status=HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return instance

    def stop_instance(self, instance):
        """
        Given an instance of ec2, tries to stop it. First, checks if the client to perform that operation
        :param instance: to be stopped
        :return: status of the instance once the stop order has been asked
        """
        try:
            instance.stop(DryRun=True)
        except ClientError as e:
            if 'DryRunOperation' not in str(e):
                raise

        return instance.stop()

    def create_vm(self, security_group_id, ami=WORDPRESS_AMI):
        """
        Creates a ec2 instance given a security group and an AMI
        :param security_group_id: to attach to the ec2 instance
        :param ami: it will the based of the instance
        :return: instance just created
        """
        try:
            self._base_create_vm(security_group_id, ami, True)
        except ClientError as e:
            if 'DryRunOperation' not in str(e):
                raise

        instances = self._base_create_vm(security_group_id, ami)
        # We are only creating one instance, so we access the index 0
        return instances[0]

    def create_security_group(self):
        """
        Routine to create a security group.
        1) Gets the VPC id, by default we take the first one.
        2) Create a security group based on the previous id. First it'll try to create a group with the hardcoded
        name, SECURITY_GROUP_NAME, if it's not available, it'll create a random one.
        3) Attaches security ingress to the group
        :return: id of the security group
        """
        try:
            vpc_id = self._get_vpc_id()

            group_name = SECURITY_GROUP_NAME

            # If there is a security group named exactly as the one hardcoded on the code, we generate a random
            # one with the hardcoded one as base plus a random uuid
            if self.security_group_exists():
                group_name += f'-{uuid4()}'
                logger.info(f'Security group with name {SECURITY_GROUP_NAME}, exists already, assigning new name '
                            f'{group_name}')

            security_group = self._create_security_group(group_name, vpc_id)

            security_group_id = security_group.id

            self._assign_security_group_ingress(security_group_id)
            return security_group_id
        except ClientError:
            raise

    def _get_vpc_id(self):
        try:
            self.get_raw_client().describe_vpcs(DryRun=True)
        except ClientError as e:
            if 'DryRunOperation' not in str(e):
                raise

        vpcs = self.get_raw_client().describe_vpcs()
        # By default, we take the first VPC
        vpc_id = vpcs.get('Vpcs', [{}])[0].get('VpcId', '')
        return vpc_id

    def _assign_security_group_ingress(self, security_group_id):
        try:
            self.__base_assign_security_group_ingress(security_group_id, True)
        except ClientError as e:
            if 'DryRunOperation' not in str(e):
                raise
        self.__base_assign_security_group_ingress(security_group_id)

    def __base_assign_security_group_ingress(self, security_group_id, checking_permissions=False):
        """
        Internal wrapper to be used by _assign_security_group_ingress so it can run in DryRun mode to check for
        permissions.
        By default we open three ports for Anywhere
        :param security_group_id: to attach IpPermissions
        :param checking_permissions: True if we want to check for permissions, False, to run the actual operation
        :return:
        """
        self.get_raw_client().authorize_security_group_ingress(
            GroupId=security_group_id,
            IpPermissions=[
                {'IpProtocol': 'tcp',
                 'FromPort': 80,
                 'ToPort': 80,
                 'IpRanges': [{'CidrIp': '0.0.0.0/0'}]},
                {'IpProtocol': 'tcp',
                 'FromPort': 443,
                 'ToPort': 443,
                 'IpRanges': [{'CidrIp': '0.0.0.0/0'}]},
                {'IpProtocol': 'tcp',
                 'FromPort': 22,
                 'ToPort': 22,
                 'IpRanges': [{'CidrIp': '0.0.0.0/0'}]},
            ],
            DryRun=checking_permissions)

        if not checking_permissions:
            logger.info(f'Security group ingress assigned for group id {security_group_id}')

    def _create_security_group(self, group_name, vpc_id):
        try:
            self.__base_create_security_group(group_name, vpc_id, True)
        except ClientError as e:
            if 'DryRunOperation' not in str(e):
                raise

        return self.__base_create_security_group(group_name, vpc_id)

    def __base_create_security_group(self, group_name, vpc_id, checking_permissions=False):
        """
        Internal wrapper to be used by create_security_group so it can run in DryRun mode to check for permissions.
        :param group_name: name of the group.
        :param vpc_id: id of the VPC, by default we use the default one
        :param checking_permissions: True if we want to check for permissions, False, to run the actual operation
        :return: security group
        """
        security_group = self.client.create_security_group(GroupName=group_name,
                                                           Description=SECURITY_GROUP_DESCRIPTION,
                                                           VpcId=vpc_id,
                                                           DryRun=checking_permissions)

        if not checking_permissions:
            logger.info(f'Security group with name {group_name}, for VPC {vpc_id}, created')

        return security_group

    def _base_create_vm(self, security_group_id, ami=WORDPRESS_AMI, checking_permissions=False):
        """
        Internal wrapper to be used by create_vm so it can run in DryRun mode to check for permissions.
        We do not assign a KeyName to this instance on launch time, meaning we will not be able to connect to it
        through ssh although permissions security was fixed to be able to do so.
        :param security_group_id: to be attached to the instance
        :param ami: to be the based of the instance
        :param checking_permissions: True if we want to check for permissions, False, to run the actual operation
        :return: ec2 instance
        """
        vm = self.client.create_instances(ImageId=ami,
                                          InstanceType='t2.micro',
                                          MinCount=1,
                                          MaxCount=1,
                                          SecurityGroupIds=[
                                              security_group_id,
                                          ],
                                          DryRun=checking_permissions)

        if not checking_permissions:
            logger.info(f'VM with AMI {ami}, type t2.micro and security group {security_group_id}')

        return vm


aws = None


def get_aws_client(client_id, client_secret, resource='ec2'):
    global aws
    try:
        if aws is None:
            aws = AmazonAPIWrapper(client_id, client_secret, resource)
    except Exception as e:
        logger.warning(f'There has been an error creating a AWS client, {e}')
        pass
    return aws
