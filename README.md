# aws-launchpad

Small proof of concept on how to launch AWS EC2 instances dynamically using AWS Credentials. The project is not
complete but, it's functional.

## Structure
It is divided in three different parts, backend, frontend and docker.For more details please, see below the complete
structure up to two levels.
```
.
├── backend
│   ├── config
│   ├── core
│   ├── ec2
│   ├── entrypoint.sh
│   ├── __init__.py
│   ├── manage.py
│   ├── requirements.in
│   ├── requirements.txt
│   ├── urls.py
│   └── wsgi.py
├── docker
│   ├── DockerfileBE
│   └── DockerfileFE
├── docker-compose.yml
└── frontend
    ├── angular.json
    ├── browserslist
    ├── e2e
    ├── karma.conf.js
    ├── nginx
    ├── node_modules
    ├── package.json
    ├── package-lock.json
    ├── README.md
    ├── src
    ├── tsconfig.app.json
    ├── tsconfig.json
    ├── tsconfig.spec.json
    └── tslint.json

```

## How to run the project?
Clone or download the repository and from the root folder `docker-compose up --build`. By default `frontend` is listening on
port `4200` and backend in `8000`.

*Important notes*: If you wish to change the port on where the host is listening to the backend, please, do remember to change it
on `frontend/src/environment/environment.{,.prod}ts`. Angular by default needs to rebuild the project if env variables are changed,
if you do so, please remember to build the frontend again, `docker-compose build frontend`.

## Prerequisites
You need to have **full access to EC2** to be able to run the project, so please, go to your Amazon Console and give the user
the needed policy.

## Notes
Once the frontend application is running and you've submitted your AWS Credentials, **do not reload the page**, if you do so,
the instance will still be created but you will not be able to see the progress on the app and will be asked to enter your
credentials again. If you go to your console, your will see how the instance is being created.

The following assumptions were taken into place:

- Instance type and region by default are `t2.micro` and `eu-west-1` respectively.
- A security group is created with the name `bitnami-wordpress-sg` is created and attached to the EC2 instance. If by any chance,
you create more instances using the app, additional security groups will be created with this pattern: `bitnami-wordpress-sg-{uuid4}`.
- Default security ingresses attached to the before mentioned security groups are:
  ```
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
  ```
  Although port `22` is open, **no AWS EC2 Key Pair** is created by this application but can be extended.
- At the time where this project was done, the latest version of Bitnami Wordpress AMI is: `ami-0ec852340933f4f48`
- Once the instance reaches the status of `Server up and running`, please note that might take a while for the given IP to be
fully accesible. At first, apart from the current check in place, a ping (security ingress was different with the addition to ICMP protocol) to the given public IP address was doing until the instance was running, but finally removed since it was not 100% representative. It could have been because of the cache of the OS or even the browser.
