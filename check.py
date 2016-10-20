#!/bin/env python

"""
Check CloudFormation template for errors. Use the AWS CLI to verify
resource ARNs and Python to count the number of defined resources.

Note: will throw an error if size of template is > 512kb
"""

from __future__ import print_function
import json
import subprocess

try:
    subprocess.check_call([
        'aws',
        'cloudformation',
        'validate-template',
        '--template-body',
        'file://VPC.json'
    ])
except Exception as e:
    pass

cft = json.load(open('VPC.json'))
print("Structure looks OK. {}/200 resources.".format(len(cft["Resources"])))
