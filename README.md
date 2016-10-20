A Sample VPC CloudFormation Template
====================================

Creates a VPC in a single region.

VPC Properties
--------------

* Three layers: Public, Application, and Data.
    - Each composed of subnets across four AZs for the given region.
    - Adjust as necessary; to remove a third AZ, find and remove `[a-z]3"$` keys.
* Internet Gateway for VPC
* NAT Gateways in all four Public Subnets
* Four Elastic IPs associated with NAT Gateways
* NACLs around all subnets
    - Configurable Public, Application, and Data ports
    - Allow all outbound traffic through NAT Gateways
    - Allow SSH to all subnets from (configurable) bastion host IP
* A single peering connection
* A single S3 endpoint in all subnets

Validation and Usage
--------------------

```bash
# Validate. Use check.py to count # of defined resources.
aws cloudformation validate-template --template-body file://VPC.json

# Launch. This command only specifies has parameters that have no defaults.
aws cloudformation create-stack --stack-name MyVPC --parameters ParameterKey=PeeringVPCId,ParameterValue=vpc-xxxxxxxx ParameterKey=BastionHostIP,ParameterValue=1.2.3.4/5 --template-body file://VPC.json
```

Other Notes
-----------

### Template Limits

* Max resources declarable by a single CF template: 200
* Max size of a resource name: 255 chars
* `awscli` complains if size of template > 512k. No issues if using S3 upload.

### Things to Do

* IAM Roles (?)
* Define some commonsensical Security Groups
* Figure out what other 'output's I need
* Draw a diagram in LucidChart

### ICMP Traffic

_Maybe_ need to add something like this for ICMP traffic between subnets? When would this be used?

```json
"NACLWorldToPublicICMPOut": {
  "Type": "AWS::EC2::NetworkAclEntry",
  "DependsOn": [
    "AssociateNACLToPublicSubnet0"
  ],
  "Properties": {
    "CidrBlock": "0.0.0.0/0",
    "NetworkAclId": {"Ref": "NACLWorldToPublic"},
    "Egress": true,
    "Protocol": 1,
    "RuleAction": "allow",
    "RuleNumber": 500
  }
},
"NACLWorldToPublicICMPIn0": {
  "Type": "AWS::EC2::NetworkAclEntry",
  "DependsOn": [
    "AssociateNACLToPublicSubnet0"
  ],
  "Properties": {
    "CidrBlock": {"Ref": "ApplicationSubnet0"},
    "NetworkAclId": {"Ref": "NACLWorldToPublic"},
    "Protocol": 1,
    "RuleAction": "allow",
    "RuleNumber": 500
  }
}
```

### Template Creation Steps

* `AWS::EC2::VPC`
* `AWS::EC2::VPCPeeringConnection`
* `AWS::EC2::InternetGateway`
    - Attach to VPC via `AWS::EC2::VPCGatewayAttachment`
* Public `AWS::EC2::Subnet` in all four zones
* App `AWS::EC2::Subnet` in all four zones
* Data `AWS::EC2::Subnet` in all four zones
* Public `AWS::EC2::RouteTable` in all four zones
    - `AWS::EC2::SubnetRouteTableAssociation` between this and Public subnets
* App `AWS::EC2::RouteTable` in all four zones
    - `AWS::EC2::SubnetRouteTableAssociation` between this and App subnets
* Data `AWS::EC2::RouteTable` in all four zones
    - `AWS::EC2::SubnetRouteTableAssociation` between this and Data subnets
* S3 Endpoint `AWS::EC2::VPCEndpoint` with all routing tables
* Four `AWS::EC2::EIP`s for all AZs
* `AWS::EC2::NatGateway`s in all four Public subnets
    - Each associated with a `AWS::EC2::EIP`
* Add `AWS::EC2::Route`s from all subnets to the `AWS::EC2::NatGateway` in their AZ
* Create `AWS::EC2::NetworkAcl`s between
    - World and Public Subnets
    - Public and App Subnets
    - App and Data Subnets
* Create `AWS::EC2::SubnetNetworkAclAssociation` between
    - All Public Subnets and World-to-Public NACL
    - All App Subnets and Public-to-App NACL
    - All Data Subnets and App-to-Data NACL
* Create `AWS::EC2::NetworkAclEntry`s
    - World-to-Public NACL
        + Allow traffic from 0.0.0.0/0 thru TCP port `PublicPort`
        + Allow all outbound traffic
        + Allow inbound SSH from `BastionHostIP`
    - Public-to-App NACL
        + Allow traffic from Public Subnet thru TCP port `ApplicationPort`
        + Allow all outbound traffic
        + Allow inbound SSH from `BastionHostIP`
    - App-to-Data NACL
        + Allow traffic from App Subnet thru TCP port `DataPort`
        + Allow all outbound traffic
        + Allow inbound SSH from `BastionHostIP`

References
----------

### Properties

* [VPC](http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-vpc.html)
* [Subnet](http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-subnet.html#d0e56476)
* [Peering Connection](http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-vpcpeeringconnection.html#d0e59558)
* [Elastic IP](http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-eip.html#d0e48482)
* [Internet Gateway](http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-internet-gateway.html)
* [VPC Gateway Attachment](http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-vpc-gateway-attachment.html#cfn-ec2-vpcgatewayattachment-internetgatewayid)
* [Subnet-to-Routing Table Attachment](http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-subnet-route-table-assoc.html#d0e57100)
* [Route](http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-route.html#d0e53835)
* [Network ACL](http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-network-acl.html#d0e51918)
* [Subnet to NACL Association](http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-subnet-network-acl-assoc.html#d0e56884)
* [A Single NACL Entry](http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-network-acl-entry.html#d0e52219)

### Miscellaneous

* [CloudFormation Conditionals](https://www.singlestoneconsulting.com/blog/2015/august/cloudformation-mapping-and-conditionals)
* [List of IANA Protocol Numbers](http://www.iana.org/assignments/protocol-numbers/protocol-numbers.xhtml)
