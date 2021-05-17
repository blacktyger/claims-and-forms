from django.conf.urls import url
from django.urls import path
from app import views


urlpatterns = [
    path('eiou_claim_confirmed/', views.EIOUClaimConfirmationView.as_view(), name='eiou_claim_confirmed'),
    path('vitex_details_handler/', views.vitex_details_handler, name='vitex_details_handler'),
    path('eiou_claim/', views.EIOUClaimView.as_view(), name='eiou_claim'),
    path('', views.HomeView.as_view(), name='home'),
    path('upload/', views.upload, name='upload')
    ]



