from rest_framework import serializers
from pzz_for_test.models import TestStoreInfo, TestPlayInfo, TestQueueInfo, TestLabelInfo, TestPlayerInfo, TestStorePlayRepoInfo

class StoreSerializer(serializers.ModelSerializer):
    class Meta:
        model = TestStoreInfo
        fields = ('store_id', 'store_name', 'store_address', 'store_contacts', 'store_tel', 'store_wechat', 'store_pic', 'store_status', 'store_info', "store_deposit")

class PlaySerializer(serializers.ModelSerializer):
    class Meta:
        model = TestPlayInfo
        fields = ('play_id', 'play_name', 'play_headcount', 'play_male_num', 'play_female_num', 'play_score', 'play_intro', 'play_img', 'play_is_original', 'play_duration')

class QueueSerializer(serializers.ModelSerializer):
    class Meta:
        model = TestQueueInfo
        fields = ('queue_id', 'queue_status', 'queue_create_time', 'queue_end_time', 'queue_current_num', 'queue_current_male_num', 'queue_current_female_num', 'queue_allow_antigender', 'store_id', 'play_id')

class LabelSerializer(serializers.ModelSerializer):
    class Meta:
        model = TestLabelInfo
        fields = ('label_id', 'label_type', 'label_content', 'play_id', 'item_id')

class PlayerSerializer(serializers.ModelSerializer):
    class Meta:
        model = TestPlayerInfo
        fields = ('player_id','player_name','player_gender','player_pic','player_wechat','queue_id')

class TestStorePlayRepoSerializer(serializers.ModelSerializer):
    class Meta:
        model = TestStorePlayRepoInfo
        fields = ('item_id', 'item_price', 'store_id', 'play_id')

## TEST API
