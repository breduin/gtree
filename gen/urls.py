from django.urls import path
from .views import PersonView, MarriageView


urlpatterns = [
    path('person/<int:pk>', PersonView.as_view(), name='personview'),
    path('marriage/<int:pk>', MarriageView.as_view(), name='marriageview'),
]
