from django.urls import path
from . import views

app_name = "lotto_app"

urlpatterns = [
    path("", views.index, name="index"),
    path("buy/", views.buy_ticket, name="buy_ticket"),
    path("my-tickets/", views.my_tickets, name="my_tickets"),
    path("check/", views.check_result, name="check_result"),

    # 관리자용
    path("lotto-admin/", views.admin_round_list, name="admin_round_list"),
    path("lotto-admin/round/<int:round_no>/", views.admin_round_detail, name="admin_round_detail"),
    path("lotto-admin/round/<int:round_no>/draw/", views.admin_draw_round, name="admin_draw_round"),
]
