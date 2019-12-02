WORDPRESS_AMI = 'ami-0ec852340933f4f48'
SECURITY_GROUP_NAME = 'bitnami-wordpress-sg'
SECURITY_GROUP_DESCRIPTION = 'Opens port 80, 443 and 22'

ERROR_GETTING_STATUS = {
    'message': 'There has been an error getting the status of the VM',
    'code': 'client-error'
}

WRONG_CREDENTIALS = {
    'message': 'Must provide AWS Credentials',
    'code': 'empty-credentials'
}
