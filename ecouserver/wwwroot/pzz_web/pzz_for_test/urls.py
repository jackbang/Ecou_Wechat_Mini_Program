from django.conf.urls import url
from rest_framework.urlpatterns import format_suffix_patterns
from pzz_for_test import views

urlpatterns = [
    url(r'^stores/$', views.test_store_list),
    url(r'^plays/$', views.test_play_list),
    url(r'^queues/$', views.test_queue_list),
    url(r'^labels/$', views.label_list.as_view()),
    url(r'^players/$', views.player_list.as_view()),
    url(r'^playrepo/$', views.test_store_play_repo),
    #url(r'^test/$', views.TestStoreInfoAPI.as_view()),
    url(r'^test/stores/(?P<pk>[0-9]+)$', views.TestStoreInfoAPI.as_view()),
    url(r'^test/stores/(?P<pk>[0-9]+)/queues/$', views.TestQueuesInStoreAPI.as_view()),
    #url(r'^test/queues/(?P<pk>[0-9]+)$', views.TestQueueInfoInStoreAPI.as_view()),
    url(r'^test/queues/(?P<queue_id>[0-9]+)$', views.TestQueuesPersonInfoAPI.as_view()),
    url(r'^test/stores/(?P<store_id>[0-9]+)/plays$', views.TestSearchPlaytoJoinAPI.as_view()),


    url(r'^test/queues/(?P<queue_id>[0-9]+)/play$', views.TestQueuesPlayDetailInfoAPI.as_view()),
    url(r'^test/queues/(?P<queue_id>[0-9]+)/players$',views.TestQueuesPersonDetailInfoAPI.as_view()),

    url(r'^test/onlogin', views.TestWechatLoginAPI.as_view()),
    url(r'^test/getPhoneNum', views.TestGetPhoneNumberAPI.as_view()),
    url(r'^test/joinQueue', views.TestJoinQueueAPI.as_view()),
    url(r'^test/queueHistory', views.TestQueueHistoryAPI.as_view()),
    url(r'^test/mineQueueHistory', views.TestMineQueueHistoryAPI.as_view()),
    url(r'^test/createQueue', views.TestCreateQueueAPI.as_view()),
    url(r'^test/check', views.TestCheckQueueAPI.as_view()),

    url(r'^test/adminLogin', views.TestAdminLoginAPI.as_view()),
    url(r'^test/adminSendSMS', views.TestSendSMSAPI.as_view()),
    url(r'^test/uploadImg', views.TestUploadFileAPI.as_view()),

    url(r'^test/total/search', views.TestTotalSearchAPI.as_view()),
    url(r'^test/store/search', views.TestStoreSearchAPI.as_view()),

    url(r'^test/queue/search', views.TestQueueSearchAPI.as_view()),
    url(r'^test/queue/get', views.TestQueueGetAPI.as_view()),

    url(r'^test/store/delete', views.TestStoreDeleteAPI.as_view()),
    url(r'^test/store/add', views.TestStoreAddAPI.as_view()),
    url(r'^test/uploadPlayWithoutImg', views.TestUploadPlayAPI.as_view()),
    url(r'^test/uploadPlayWithImg', views.TestUploadPlayWithImgAPI.as_view()),
    url(r'^test/store/admins', views.TestStoreAdminInfoAPI.as_view()),

    url(r'^test/admin/stores', views.TestGetStoreListAPI.as_view()),

    url(r'^test/store/verify', views.TestVerifyStoreAPI.as_view()),
    url(r'^test/store/share', views.TestShareStoreAPI.as_view()),

    url(r'^test/admin/add', views.TestAddAdminAPI.as_view()),
    url(r'^test/admin/delete', views.TestDeleteAdminAPI.as_view()),

    url(r'^test/stores/(?P<store_id>[0-9]+)/unlockedQueues/$', views.TestStoreQueueListAPI.as_view()),
    url(r'^test/stores/(?P<store_id>[0-9]+)/lockedQueues/$', views.TestStoreLockedQueueListAPI.as_view()),

    url(r'^test/queue/lock', views.TestLockQueueAPI.as_view()),
    url(r'^test/queue/delock', views.TestDelockQueueAPI.as_view()),
    url(r'^test/queue/delete', views.TestDeleteQueueAPI.as_view()),

    url(r'^test/queue/players/get',views.TestAdminQueuePlayerListAPI.as_view()),
    url(r'^test/queue/players/add',views.TestAdminQueueAddPlayerAPI.as_view()),
    url(r'^test/queue/players/pop',views.TestAdminQueuePopPlayerAPI.as_view()),

    url(r'^test/saveStoreWithImg', views.TestSaveStoreWithImgAPI.as_view()),
    url(r'^test/saveStoreWithoutImg', views.TestSaveStoreWithoutImgAPI.as_view()),
    
    url(r'^stores/(?P<store_index>[0-9]+)$', views.test_store_api),
    url(r'^stores/(?P<store_index>[0-9]+)/queues/$', views.test_store_queue_api),
    url(r'^stores/(?P<store_index>[0-9]+)/queues/(?P<queue_index>[0-9]+)/play$', views.test_queue_play_api),
]

urlpatterns = format_suffix_patterns(urlpatterns)