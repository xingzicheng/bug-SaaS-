from qcloud_cos import CosConfig
from qcloud_cos import CosS3Client
from django.conf import settings

def create_bucket(bucket,region="ap-nanjing"):
    """
    创建桶
    :param bucket: 桶名称
    :param region: 区域
    :return:
    """
    secret_id = settings.TENCENT_COS_ID  # 替换为用户的 secretId
    secret_key = settings.TENCENT_COS_KEY  # 替换为用户的 secretKey

    #region = 'ap-nanjing'  # 替换为用户的 Region

    config = CosConfig(Region=region, SecretId=secret_id, SecretKey=secret_key)

    client = CosS3Client(config)

    response = client.create_bucket(
        Bucket=bucket,
        ACL="public-read"  #  private  /  public-read / public-read-write
    )


def upload_file(bucket, region, file_object, key):

    secret_id = settings.TENCENT_COS_ID  # 替换为用户的 secretId
    secret_key = settings.TENCENT_COS_KEY  # 替换为用户的 secretKey

    config = CosConfig(Region=region, SecretId=secret_id, SecretKey=secret_key)
    client = CosS3Client(config)

    response = client.upload_file_from_buffer(
        Bucket=bucket,
        Body=file_object,  # 文件对象
        Key=key  # 上传到桶之后的文件名
    )

    # https://wangyang-1251317460.cos.ap-chengdu.myqcloud.com/p1.png
    # 上传至对象存储，返回该图片的url
    return "https://{}.cos.{}.myqcloud.com/{}".format(bucket, region, key)