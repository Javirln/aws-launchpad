from botocore.exceptions import ClientError
from rest_framework.status import HTTP_400_BAD_REQUEST, HTTP_401_UNAUTHORIZED

from core.api import get_aws_client
from core.exceptions import AWSPermissionDenied


class AmazonService(object):

    @staticmethod
    def create_vm(client_id, client_secret):
        """
        Given a client id and client secret, creates a running ec2 instance. This method performs the following
        operations:
        1) Creates a security group
        2) Creates the ec2 instance with the previous security group attached
        :param client_id: AWS credential
        :param client_secret: AWS credential
        :return: {
            'InstanceId': id of the just created ec2 instance
            'InstanceType': type of the instance, by default as hardcoded, t2.micro
            'Region': region where the ec2 instance was launched, by default and as hardcoded, 'eu-west-1'
        }
        """
        aws_client = AmazonService._get_client_resource(client_id, client_secret)

        try:
            security_group_id = aws_client.create_security_group()
            instance = aws_client.create_vm(security_group_id)

            return {
                'InstanceId': instance.id,
                'InstanceType': instance.instance_type,
                'Region': instance.placement.get('AvailabilityZone', '')
            }
        except (ClientError, Exception) as e:
            AmazonService._handle_error(e)

    @staticmethod
    def stop_instance(instance_id, client_id, client_secret):
        """
        Given an instance id, client id and client secret, stops  the instance
        :param instance_id: given by AWS
        :param client_id: AWS credential
        :param client_secret: AWS credential
        :return: {
            'Code': status code,
            'Raw': status raw name given by AWS,
            'Name': pretty name for frontend to displayed
            'PublicIP': ip of the ec2 instance given by AWS,
            'Region': region where the ec2 instance was launched, by default and as hardcoded, 'eu-west-1'
        }
        """
        aws_client = AmazonService._get_client_resource(client_id, client_secret)

        try:
            instance = aws_client.get_instance(instance_id)

            if instance is None:
                raise AWSPermissionDenied('There has been an error getting the status of the VM',
                                          status=HTTP_400_BAD_REQUEST)

            instance_status = aws_client.stop_instance(instance)

            state = instance_status.get('StoppingInstances', [{}])[0].get('CurrentState')

            return {
                'Code': state.get('Code', ''),
                'Raw': state.get('Name', ''),
                'Name': AmazonService._normalize_status(state),
                'PublicIP': instance.public_ip_address,
                'InstanceType': instance.instance_type,
                'Region': instance.placement.get('AvailabilityZone', '')
            }
        except (ClientError, Exception) as e:
            AmazonService._handle_error(e)

    @staticmethod
    def get_instance_status(instance_id, client_id, client_secret):
        """
        Given an instance id, client id and client secret, checks for the status of the retrieved instance
        :param instance_id: given by AWS
        :param client_id: AWS credential
        :param client_secret: AWS credential
        :return: {
            'Code': status code,
            'Raw': status raw name given by AWS,
            'Name': pretty name for frontend to displayed
            'PublicIP': ip of the ec2 instance given by AWS,
            'Region': region where the ec2 instance was launched, by default and as hardcoded, 'eu-west-1'
        }
        """
        aws_client = AmazonService._get_client_resource(client_id, client_secret)

        try:
            instance = aws_client.get_instance(instance_id)

            if instance is None:
                raise AWSPermissionDenied('There has been an error getting the status of the VM',
                                          status=HTTP_400_BAD_REQUEST)

            state = instance.state

            return {
                'Code': state.get('Code', ''),
                'Raw': state.get('Name', ''),
                'Name': AmazonService._normalize_status(state),
                'PublicIP': instance.public_ip_address,
                'InstanceType': instance.instance_type,
                'Region': instance.placement.get('AvailabilityZone', '')
            }
        except (ClientError, Exception) as e:
            AmazonService._handle_error(e)

    @staticmethod
    def _get_client_resource(client_id, client_secret):
        aws_client = get_aws_client(client_id, client_secret)
        if not aws_client:
            raise AWSPermissionDenied("The given credentials does not have permissions to access EC2. Please,"
                                      "grant full access to EC2 to the given credentials", status=HTTP_401_UNAUTHORIZED)
        return aws_client

    @staticmethod
    def _handle_error(e):
        """
        Parses the given exception to know if it's a permissions exception or something else. If it's a permissions
        error we sent AWSPermissionDenied otherwise, the raw exception.
        :param e: exception to be parsed
        """
        if isinstance(e, ClientError):
            error_code = e.response.get('Error', {}).get('Code', '')
            if error_code == 'UnauthorizedOperation' or error_code == 'AuthFailure':
                raise AWSPermissionDenied("You don't have permissions to perform this operation",
                                          status=HTTP_401_UNAUTHORIZED)
            raise

    @staticmethod
    def _normalize_status(state):
        """
        Parses incoming instance status and prettify its name
        :param state: raw state
        :return: final name
        """
        raw_name = state.get('Name')
        label = ''
        if raw_name == 'pending':
            label = 'Launching server'
        elif raw_name == 'running':
            label = 'Server up and running'
        elif raw_name == 'shutting-down':
            label = 'Shutting down server'
        elif raw_name == 'stopped':
            label = 'Server stopped'
        elif raw_name == 'stopping':
            label = 'Stopping server'
        elif raw_name == 'terminated':
            label = 'Server is terminated'
        return label
