import boto3


def create_instance(key,secrete,region,availablity_zone,ami_id1,instance_type1,ec2_instance_keyname1,boto_instance_profile1):

    ec2_client = boto3.client("ec2", region_name=region,aws_access_key_id=key,aws_secret_access_key=secrete)

    #vpc creation with IP block 10.0.0.0/16 you can change CidrBlock to custom ip subnet range
    vpc_1 = ec2_client.create_vpc(
             CidrBlock='10.0.0.0/16',
           )
    print("vpc id: "+vpc_1["Vpc"]["VpcId"])

    #create one subnet with availablilty zone as availablity_zone. You can change CidrBlock according to vpc CidrBlock
    subnet_1 = ec2_client.create_subnet(
             AvailabilityZone=availablity_zone,
             CidrBlock='10.0.1.0/24',
             VpcId=vpc_1["Vpc"]["VpcId"]
            )
    print("subnet_id :"+subnet_1["Subnet"]["SubnetId"])

    #create internet gateway
    internet_gateway_1=ec2_client.create_internet_gateway()
    print("internet gateway id :"+internet_gateway_1["InternetGateway"]["InternetGatewayId"]) 

    #attach internet gateway to vpc
    internet_attachment_1 = ec2_client.attach_internet_gateway(
               InternetGatewayId=internet_gateway_1["InternetGateway"]["InternetGatewayId"],
               VpcId=vpc_1["Vpc"]["VpcId"]
             )
    print("internet gateway response meta data :"+str(internet_attachment_1))

    #route table creation
    route_table_1 = ec2_client.create_route_table(VpcId=vpc_1["Vpc"]["VpcId"])
    print("route table id: "+route_table_1["RouteTable"]["RouteTableId"])

    #route table association with subnet
    route_table_asso_1 = ec2_client.associate_route_table(
                        RouteTableId=route_table_1["RouteTable"]["RouteTableId"],
                        SubnetId=subnet_1["Subnet"]["SubnetId"]
                        )
    print("route table association response meta data :"+str(route_table_asso_1))

    #create routes in route table (here internet gateway associated with subnet in route table to have public access)
    route_create_1 = ec2_client.create_route(
                       DestinationCidrBlock='0.0.0.0/0',
                       GatewayId=internet_gateway_1["InternetGateway"]["InternetGatewayId"],
                       RouteTableId=route_table_1["RouteTable"]["RouteTableId"],
                      )
    print("route creation response meta data :"+str(route_create_1))



    #security group creation
    security_group = ec2_client.create_security_group(
    Description='Allow inbound SSH traffic',
    GroupName='allow-inbound-ssh',
    VpcId=vpc_1["Vpc"]["VpcId"],
    TagSpecifications=[
        {
            'ResourceType': 'security-group',
            'Tags': [
                {
                    'Key': 'Name',
                    'Value': 'allow-inbound-ssh'
                },
            ]
        },
      ],
      )
    #authorized ingress with security group - all inbound ssh
    response = ec2_client.authorize_security_group_ingress(
    GroupId=security_group["GroupId"],
    IpPermissions=[
        {
            'FromPort': 22,
            'IpProtocol': 'tcp',
            'ToPort': 22,
            'IpRanges': [
                {
                    'CidrIp': '0.0.0.0/0',
                    'Description': 'inbound ssh'
                },
             ],
            'UserIdGroupPairs': [
                {
                    'Description': 'SSH access',
                    'GroupId': security_group["GroupId"],
                },
            ],
        }

      ],
     )

    print(response)
    print('Security Group has been created: '+security_group["GroupId"])



    #instance creation
    ec2_resouce1=boto3.resource("ec2", region_name=region,aws_access_key_id=key,aws_secret_access_key=secrete)
    instances=ec2_resouce1.create_instances(
                     MinCount = 1,
                     MaxCount = 1,
                     ImageId=ami_id1,
                     InstanceType=instance_type1,
                     KeyName=ec2_instance_keyname1,
                     #UserData=USER_DATA, ## you can put bash shellscript in USER_DATA variable to run command during  instance intialization
                     NetworkInterfaces=[
                      {   "DeviceIndex": 0,
                          "AssociatePublicIpAddress": True,
                          "Groups": [security_group["GroupId"]],
                          "SubnetId": subnet_1["Subnet"]["SubnetId"]

                      }],
                     TagSpecifications=[
                       {
                        'ResourceType': 'instance',
                        'Tags': [
                         {
                           'Key': 'Name',
                           'Value': 'my-ec2-instance'
                         },
                         ]
                      },
                    ]
                   )
    # setup instance profile and start ec2 instance
    for instance in instances:
            print(f'EC2 instance "{instance.id}" has been launched')
            instance.wait_until_running()
            ec2_client.associate_iam_instance_profile(
                  IamInstanceProfile = {'Name': boto_instance_profile1 },
                  InstanceId = instance.id,
                  )
            print('EC2 Instance Profile boto-profile has been attached')
            waiter = ec2_client.get_waiter('system_status_ok')
            waiter.wait(InstanceIds=[instance.id])
            waiter = ec2_client.get_waiter('instance_status_ok')
            waiter.wait(InstanceIds=[instance.id])
            instance.reload()
            print(f'EC2 instance "{instance.id}" has been started')
            print(f'EC2 instance public ip is {instance.public_ip_address}')

    #find running instance whch has tag 'my-ec2-instance'
    find_instance1 = ec2_client.describe_instances(
       Filters=[
            {
                'Name': 'tag:Name',
                'Values': ['my-ec2-instance']
            }
        ]
      )

    print("#############")
    for reservation in (find_instance1["Reservations"]):
        for instance in reservation["Instances"]:
            if instance["State"]["Name"] == "running":
               print(instance["InstanceId"],instance["State"]["Name"])

def destroy_instance(instanceid,region,key,secrete):
    ec2_client = boto3.client("ec2", region_name=region,aws_access_key_id=key,aws_secret_access_key=secrete)
    response = ec2_client.terminate_instances(
                InstanceIds=[ intanceid ],
                DryRun=False
    )

    print('response: '+response)


def destroy_vpc(vpcid,region,key,secrete):

    ec2_client = boto3.client("ec2", region_name=region,aws_access_key_id=key,aws_secret_access_key=secrete)
    response = ec2_client.delete_vpc(
               VpcId=vpcid,
               )
    print(str(response))


# create_instance will create vpc, subnet (public subnet creation via creating and attaching internet gateway to subnet via creating route table with route association with internet gateway), security group with rules to allow ssh traffic, 1 ec2 instance (can change min max in ec2_resouce1 to create more than one ec2 instance) with public ip having instance tag 'my-ec2-instance'. It will also display running instance with tag 'my-ec2-instance'. At completion of this funcion create_instance it will display vpcid,instance id and other created resource ids.
create_instance(key,secrete,region,availablity_zone,ami_id1,instance_type1,ec2_instance_keyname1,boto_instance_profile1)
## here in create_instance - key is aws_key_id,secrete is aws_secrete_access, region is aws region with availability zone as availablity_zone, instance_type1 is instance type, instance_keyname1 (must pre-exist, we can create using boto library before instance creation) is ssh key to assoiciate with ec2 instance, ami_id1 is ami image id, boto_instance_profile1 is  instance profile to associate with instance
 

# It will destroy perticular instance having instance id as instanceid in region region  having  key is aws_key_id and secrete is aws_secrete_access
destroy_instance(instanceid,region,key,secrete)
# it will display  response of instance destruction
# first delete ec2 then VPC incase of removing whole vpc and ec2 instance

# it will destroy perticular vpc having vpcid as vpcid in region region havig key is aws_key_id and secrete is aws_secrete_access
destroy_vpc(vpcid,region,key,secrete)
# it will display response of vpcid destruction
