from django.db import models

# Create your models here.
class TestStoreInfo(models.Model):
    store_id = models.AutoField(primary_key=True)
    store_name = models.CharField(max_length=20, blank=True, default='')
    store_address = models.CharField(max_length=50, blank=True, default='')
    store_contacts = models.CharField(max_length=10, blank=True, default='')
    store_tel = models.CharField(max_length=15, blank=True, default='')
    store_wechat = models.CharField(max_length=20, blank=True, default='')
    store_pic = models.TextField(blank=True, default='')
    store_created = models.DateTimeField(auto_now_add=True)
    store_status = models.PositiveSmallIntegerField(default=0)
    store_info = models.CharField(max_length=25, blank=True, default='')
    store_deposit = models.PositiveSmallIntegerField(default=0)
    store_latitude = models.FloatField(default=0)
    store_longitude = models.FloatField(default=0)
    store_position = models.CharField(max_length=20, blank=True, default='')
    store_tel2 = models.CharField(max_length=15, blank=True, default='')
    class Meta:
        ordering = ('store_created',)

class TestPlayInfo(models.Model):
    play_id = models.AutoField(primary_key=True)
    play_name = models.CharField(max_length=20, blank=True, default='')
    play_headcount = models.PositiveSmallIntegerField(blank=True, default=0)
    play_male_num = models.PositiveSmallIntegerField(blank=True, default=0)
    play_female_num = models.PositiveSmallIntegerField(blank=True, default=0)
    play_score = models.PositiveSmallIntegerField(blank=True, default=3)
    play_intro = models.TextField(blank=True, default='')
    play_img = models.TextField(blank=True, default='')
    play_is_original = models.BooleanField(blank=True, default=False)
    play_created = models.DateTimeField(auto_now_add=True)
    play_duration = models.PositiveSmallIntegerField(default=3)
    play_antigender = models.BooleanField(default=False)
    class Meta:
        ordering = ('play_created',)

class TestUserInfo(models.Model):
    user_id = models.AutoField(primary_key=True)
    user_openid = models.CharField(max_length=32, default="")
    user_gender = models.PositiveSmallIntegerField(default=0)
    user_nickName = models.CharField(max_length=30, default="")
    user_avatarUrl = models.TextField(blank=True, default='')
    user_province = models.CharField(max_length=16, blank=True, default='')
    user_city = models.CharField(max_length=32, blank=True, default='')
    user_phoneNum = models.CharField(max_length=15, blank=True, default='')
    user_purePhoneNum = models.CharField(max_length=20, blank=True, default='')
    user_countryCode = models.CharField(max_length=25, blank=True, default='')
    user_lastLoginTime = models.DateTimeField()
    user_lastLoginSysInfo = models.TextField(blank=True, default='')
    user_lastLoginIp = models.CharField(max_length=16, blank=True, default='')
    user_lastModifiedTime = models.DateTimeField(auto_now = True)
    user_lastSessionKey = models.CharField(max_length=32, default="")
    user_last3rdSession = models.CharField(max_length=32, default="")
    user_createTime = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('user_createTime',)

class TestAdminInfo(models.Model):
    admin_id = models.AutoField(primary_key=True)
    admin_openid = models.CharField(max_length=32, default="")
    admin_gender = models.PositiveSmallIntegerField(default=0)
    admin_nickName = models.CharField(max_length=30, default="")
    admin_avatarUrl = models.TextField(blank=True, default='')
    admin_province = models.CharField(max_length=16, blank=True, default='')
    admin_city = models.CharField(max_length=32, blank=True, default='')
    admin_phoneNum = models.CharField(max_length=15, blank=True, default='')
    admin_purePhoneNum = models.CharField(max_length=20, blank=True, default='')
    admin_countryCode = models.CharField(max_length=25, blank=True, default='')
    admin_lastLoginTime = models.DateTimeField()
    admin_lastLoginSysInfo = models.TextField(blank=True, default='')
    admin_lastLoginIp = models.CharField(max_length=16, blank=True, default='')
    admin_lastModifiedTime = models.DateTimeField(auto_now = True)
    admin_lastSessionKey = models.CharField(max_length=32, default="")
    admin_last3rdSession = models.CharField(max_length=32, default="")
    admin_createTime = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('admin_createTime',)

class TestAdminStoreInfo(models.Model):
    adminStore_id = models.AutoField(primary_key=True)
    adminStore_name = models.CharField(max_length=5, blank=True, default='')
    adminStore_idCard = models.CharField(max_length=18, blank=True, default='')
    adminStore_phone = models.CharField(max_length=15, blank=True, default='')
    adminStore_verify = models.SmallIntegerField(default=0)
    admin_id = models.ForeignKey(TestAdminInfo, on_delete=models.CASCADE, default=1, related_name='all_adminStores')
    store_id = models.ForeignKey(TestStoreInfo, on_delete=models.CASCADE, default=1, related_name='all_admins')
    adminStore_permission = models.SmallIntegerField(default=0)
    '''
    0 is staff
    1 is owner
    '''
    adminStore_createTime = models.DateTimeField(auto_now_add=True)
    class Meta:
        ordering = ('adminStore_createTime',)

class TestQueueInfo(models.Model):
    queue_id = models.AutoField(primary_key=True)
    queue_status = models.SmallIntegerField(default=0)
    queue_create_time = models.DateTimeField(auto_now_add=True)
    queue_end_time = models.DateTimeField()
    queue_current_num = models.SmallIntegerField(default=0)
    queue_current_male_num = models.SmallIntegerField(default=0)
    queue_current_female_num = models.SmallIntegerField(default=0)
    queue_allow_antigender = models.BooleanField(default=False)
    store_id = models.ForeignKey(TestStoreInfo, on_delete=models.SET_DEFAULT, default=1, related_name='all_queues')
    play_id = models.ForeignKey(TestPlayInfo, on_delete=models.SET_DEFAULT, default=1, related_name='all_queues')
    class Meta:
        ordering = ('queue_create_time',)

class TestStorePlayRepoInfo(models.Model):
    item_id = models.AutoField(primary_key=True)
    item_price = models.PositiveSmallIntegerField(default=0)
    store_id = models.ForeignKey(TestStoreInfo, on_delete=models.CASCADE, default=1, related_name='all_plays')
    play_id = models.ForeignKey(TestPlayInfo, on_delete=models.CASCADE, default=1, related_name='all_stores')
    item_create_time = models.DateTimeField(auto_now_add=True)
    class Meta:
        ordering = ('item_create_time',)

class TestLabelInfo(models.Model):
    label_id = models.AutoField(primary_key=True)
    label_type = models.PositiveSmallIntegerField(default=0)
    label_content = models.CharField(max_length=5, default="")
    play_id = models.ForeignKey(TestPlayInfo, on_delete=models.CASCADE, default=1, related_name='all_labels')
    item_id = models.ForeignKey(TestStorePlayRepoInfo, on_delete=models.CASCADE, default=1, related_name='all_labels')
    label_create_time = models.DateTimeField(auto_now_add=True)
    class Meta:
        ordering = ('label_create_time',)

class TestPlayerInfo(models.Model):
    player_id = models.AutoField(primary_key=True)
    player_name = models.CharField(max_length=10, default="")
    player_gender = models.PositiveSmallIntegerField(default=0)
    player_pic = models.TextField(blank=True, default='')
    player_wechat = models.CharField(max_length=20, blank=True, default='')
    player_tel = models.CharField(max_length=16, blank=True, default='')
    player_comment = models.TextField(blank=True, default='')
    queue_id = models.ForeignKey(TestQueueInfo, on_delete=models.CASCADE, default=1, related_name='all_players')
    user_id = models.ForeignKey(TestUserInfo, on_delete=models.SET_DEFAULT, default=1, related_name='all_players')
    player_time = models.DateTimeField(auto_now_add=True)
    class Meta:
        ordering = ('player_time',)


