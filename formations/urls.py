from django.urls import path

from formations import views

urlpatterns = [
    path("catalogue/", views.FormationsListView.as_view(), name="formations_list"),
]
