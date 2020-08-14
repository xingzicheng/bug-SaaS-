import base
from web import models

def run():
        models.PricePolicy.objects.filter(category=1).update(
            category=1,
            title="个人免费版",
            price=0,
            project_num=3,
            project_member=20,
            project_space=20,
            per_file_size=5
        )


if __name__ == '__main__':
    run()
