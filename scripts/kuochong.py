import base
from web import models
# 测试时项目成员不够用，扩充一下，注意id=1必须为个人免费版
def run():
        models.PricePolicy.objects.filter(id=1, category=1).update(
            category=1,
            title="个人免费版",
            price=0,
            project_num=3,
            project_member=20,
            project_space=20,
            per_file_size=5
        )


if __name__ == '__main__':
    #run()
