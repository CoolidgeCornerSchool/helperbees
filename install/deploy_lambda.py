#!/usr/bin/env python3

"""
 Script to deploy lambdas
"""

import os
import boto3
import subprocess
from settings import ROOT_DIR, S3_BUCKET, INSTALL_DIR, ENV, CLEAN_BUILD

S3 = boto3.client('s3')
S3_ZIP_FILE = 'functions.zip'

# hack: AWS template can't reference sibling dirs
BUILD_DIR = INSTALL_DIR
LOCAL_ZIP_PATH  = os.path.join(os.path.abspath(BUILD_DIR), 'functions.zip')

LAMBDA = boto3.client('lambda')

FUNCTIONS = [ 'user_get', 'user_get_all', 'user_create', 'user_update', 'user_delete', 'user_login',
              'offer_create_with_user',
              'offer_get', 'offer_get_all', 'offer_update', 'offer_delete',
              'order_create', 'order_get', 'order_get_all', 'order_delete',
              'get_swagger' ] 

def upload_artifact(env, local_filename, s3_filename):
    key = f'{env}/artifacts/{s3_filename}'
    S3.upload_file(local_filename, S3_BUCKET, key)

def deploy(env):
    """
    If env='prd', uploads to S3
    If env='dev', assumes local dev with SAM
    """
    # Zip package
    if CLEAN_BUILD and os.path.exists(LOCAL_ZIP_PATH):
        os.remove(LOCAL_ZIP_PATH)

    if not os.path.exists(LOCAL_ZIP_PATH):
        zip_lib_cmd = ['zip', '-r9', LOCAL_ZIP_PATH, 'lib/']
        subprocess.call(zip_lib_cmd, cwd=ROOT_DIR)

    zip_cmd = ['zip', '-r9', LOCAL_ZIP_PATH, '.', '-x', '*~']
    subprocess.call(zip_cmd, cwd=os.path.join(ROOT_DIR, 'functions'))
    
    if env == 'prd':
        # Upload to S3
        upload_artifact(env, LOCAL_ZIP_PATH, S3_ZIP_FILE)
        # Update functions
        for function in FUNCTIONS:
            key = f'prd/artifacts/{S3_ZIP_FILE}'
            print(f'Updating {function} lambda code')

            LAMBDA.update_function_code(
                FunctionName=function,
                S3Bucket=S3_BUCKET,
                S3Key=key,
                Publish=True
                )

if __name__ == '__main__':
    # Use 'prd' to push code to S3 instead of keeping it locally
    deploy(ENV)
