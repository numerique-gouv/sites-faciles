from django.urls import path

from formations import views

urlpatterns = [
    path("catalogue/", views.FormationsListView.as_view(), name="formations_list"),
    path("booster-agile-chatbot/", views.BoosterAgileChatbotView.as_view(), name="booster_agile_chatbot"),
]
