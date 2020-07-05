from qcloud_cos import CosConfig
from qcloud_cos import CosS3Client

#上传到对象存储

secret_id = "COS的secret_id"  # 替换为用户的 secretId
secret_key = "COS的secret_key"  # 替换为用户的 secretKey

region = 'ap-nanjing'  # 替换为用户的 Region

config = CosConfig(Region=region, SecretId=secret_id, SecretKey=secret_key)

client = CosS3Client(config)

response = client.upload_file(
    Bucket='xingzicheng-1302500805',
    LocalFilePath='D:\图片\pygame.jpg',  # 本地文件的路径
    Key='p1.png'  # 上传到桶之后的文件名
)
print(response['ETag'])