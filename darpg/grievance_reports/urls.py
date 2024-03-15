from django.urls import path
from grievance_reports import views

urlpatterns = [
    path("", views.landing, name="landing"),
    path("report", views.report, name='report'),
    path("portal", views.portal, name='portal'),
    path("chatbot", views.chatbot, name='chatbot'),
]