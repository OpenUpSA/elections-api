from django.conf.urls.defaults import url, patterns, include
from django.contrib.auth.models import User, Group
from rest_framework import viewsets, routers
import views


from django.contrib import admin
admin.autodiscover()

# Routers provide an easy way of automatically determining the URL conf
router = routers.DefaultRouter()
router.register(r'events', views.EventViewSet)
router.register(r'provinces', views.ProvinceViewSet)
router.register(r'municipalities', views.MunicipalityViewSet)
router.register(r'wards', views.WardViewSet)
router.register(r'voting_districts', views.VotingDistrictViewSet)
router.register(r'parties', views.PartyViewSet)
router.register(r'results', views.ResultViewSet)
router.register(r'flat_results', views.FlatResultViewSet)
router.register(r'result_summaries', views.ResultSummaryViewSet)
router.register(r'votes/by_voting_district', views.VotingDistrictVotesViewSet)
router.register(r'votes/by_ward', views.WardVotesViewSet)
router.register(r'votes/by_municipality', views.MunicipalityVotesViewSet)
router.register(r'votes/by_province', views.ProvinceVotesViewSet)

urlpatterns = patterns('',
    url(r'^admin/', include(admin.site.urls)),
    url(r'^', include(router.urls)),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
)
