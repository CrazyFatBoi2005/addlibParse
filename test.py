# import boto3
# from botocore.client import Config
#
#
# s3_client = boto3.client(
#     's3',
#     endpoint_url='https://s3.timeweb.com',
#     region_name='ru-1',
#     aws_access_key_id='it27776',
#     aws_secret_access_key='1cad6c15403631a01cc0bf26a5ce1524',
#     config=Config(s3={'addressing_style': 'path'})
# )
#
# file_path = "temporary_storage/oly/a.txt"
# bucket_name = "7b3ae2a6-1e521fbf-430f-4275-aea8-858d0059469b"
#
# s3_client.upload_file(f'{file_path}', bucket_name, f"Alo_Yoga/a.txt")