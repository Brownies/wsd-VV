# urls.py for VidyaVortex project 2015-2016

from django.conf.urls import url
from DataVortex import views
from django.contrib.auth.views import login, logout

urlpatterns = [
    url(r'^$', views.home, name="homepage"),
    url(r'^faq/$', views.faq, name="faqpage"),
    url(r'^register/$', views.register, name="register"),
    url(r'^login/$', login, {'template_name': 'DataVortex/login.html'}, name="login"),
    url(r'^logout/$', logout, {'next_page': 'homepage'}, name="logout"),
    url(r'^playgame/(\d+)/$', views.playgame, name="playgame"),
    url(r'^ajax/$', views.ajax, name="ajax"),
    url(r'^addgame/$', views.addgame, name='addgame'),
    url(r'^browse/$', views.browse, name='browse'),
    url(r'^purchase/(\d+)/$', views.purchase, name="purchase"),
    url(r'^purchase_failed/$', views.purchase_failed, name="purchase_failed"),
    url(r'^purchase_successful/$', views.purchase_successful, name="purchase_successful"),
    url(r'^delete/(\d+)/$', views.delete, name="delete"),
    url(r'^highscores/$', views.highscores, name='highscores'),
    url(r'^editgame/(\d+)/$', views.editgame, name="editgame"),
    url(r'^salesinfo/(\d+)/$', views.salesinfo, name="salesinfo"),
    url(r'^verify/$', views.verify, name='verify'),
    url(r'^api/$', views.api, name='api')
]
