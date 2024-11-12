This POC (Proof Of Concept) is created to demostrate how Python3 - boto3 can be used for AWS resource creation and destruction. Here Boto3 Python3 code is shown for "AWS VPC creation from scratch ,One public Subnet creation from scratch, Internet Gateway, Route Table creation from scratch, Routes in Route table creation from scratch, Security group with security rules (example ssh inbound access rule) creation from scratch,destruction of instance with perticular instance id and  destruction of VPC with perticular vpcid". This is small code and there are many inhancement possible in this code. Its just showcase of my Boto3 Python3 and AWS service automation  skills that shows that I can deliver more and I have adequate understanding/ability of AWS and Python3 Boto3 code.



---------------- Code Usage ------------

1)create_instance(key,secrete,region,availablity_zone,ami_id1,instance_type1,ec2_instance_keyname1,boto_instance_profile1)
1.1) 
create_instance will create vpc, subnet (public subnet creation via creating and attaching internet gateway to subnet via creating route table with route association with internet gateway), security group with rules to allow ssh traffic, 1 ec2 instance (can change min max in ec2_resouce1 to create more than one ec2 instance) with public ip having instance tag 'my-ec2-instance'. It will also display running instance with tag 'my-ec2-instance'. At completion of this funcion create_instance it will display vpcid,instance id and other created resource ids.
1.2)
here in create_instance - key is aws_key_id,secrete is aws_secrete_access, region is aws region with availability zone as availablity_zone, instance_type1 is instance type, instance_keyname1 (must pre-exist, we can create using boto library before instance creation) is ssh key to assoiciate with ec2 instance, ami_id1 is ami image id, boto_instance_profile1 is  instance profile to associate with instance

2)destroy_instance(instanceid,region,key,secrete)
2.1)
It will destroy perticular instance having instance id as instanceid in region region  having  key is aws_key_id and secrete is aws_secrete_access
2.2)
it will display  response of instance destruction

3)destroy_vpc(vpcid,region,key,secrete)
3.1) 
it will destroy perticular vpc having vpcid as vpcid in region region havig key is aws_key_id and secrete is aws_secrete_access
3.2) 
it will display response of vpcid destruction

