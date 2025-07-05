from peewee import *
from user_srv.settings import setting

class BaseModel(Model):
    class Meta:
        database = setting.DB

GENDER_CHOICES = (
    ("female", '女'),
    ("male", '男'),
)
ROLE_CHOICES = (
    (1, '普通用户'),
    (2, '管理员'),
)
class User(BaseModel):
    mobile = CharField(max_length=20, index=True, unique=True, verbose_name='手机号码')
    password = CharField(max_length=100, verbose_name='密码')
    nick_name = CharField(max_length=20, null=True, verbose_name='昵称')
    head_url = CharField(max_length=200, null=True, verbose_name='头像')
    birthday = DateField(null=True, verbose_name='生日')
    address =  CharField(max_length=200, null=True, verbose_name='地址')
    desc =  TextField(null=True, verbose_name='个人简介')
    gender = CharField(max_length=10, choices=GENDER_CHOICES, null=True, verbose_name='性别')
    role = IntegerField(default=1, choices=ROLE_CHOICES, verbose_name='用户角色')


if __name__ == '__main__':
    # 首先创建表
    if True:
        from passlib.hash import pbkdf2_sha256
        from datetime import date

        # 创建表
        db = setting.DB
        db.create_tables([User])

        # 插入一条生日为今天的数据
        user = User()
        user.nick_name = '今日用户'
        user.mobile = '13888888888'
        user.password = pbkdf2_sha256.hash('admin123')
        user.birthday = date.today()  # 今天的日期
        user.gender = 'male'
        user.address = '北京市朝阳区'
        user.desc = '今天生日的测试用户'
        user.save()

        print(f"插入成功！用户: {user.nick_name}, 生日: {user.birthday}")

    if False:
        for user in User.select():
            import time
            from datetime import datetime
            if user.birthday:
                print(user.birthday)
                # 将字符串转换为 datetime 对象
                # 假设生日格式是 YYYY-MM-DD，如果格式不同请调整
                try:
                    birthday_date = datetime.strptime(user.birthday, '%Y-%m-%d')
                    u_time = time.mktime(birthday_date.timetuple())
                    print(u_time)
                except ValueError as e:
                    print(f"日期格式错误: {user.birthday}, 错误: {e}")
                    # 尝试其他常见格式
                    try:
                        birthday_date = datetime.strptime(user.birthday, '%Y/%m/%d')
                        u_time = time.mktime(birthday_date.timetuple())
                        print(u_time)
                    except ValueError:
                        print(f"无法解析日期格式: {user.birthday}")