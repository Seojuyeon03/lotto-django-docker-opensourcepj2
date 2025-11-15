from django.contrib import admin
from .models import LottoRound, LottoTicket

@admin.register(LottoRound)
class LottoRoundAdmin(admin.ModelAdmin):
    list_display = ("round_no", "draw_date", "n1", "n2", "n3", "n4", "n5", "n6", "bonus")
    search_fields = ("round_no",)


@admin.register(LottoTicket)
class LottoTicketAdmin(admin.ModelAdmin):
    list_display = ("round", "buyer_name", "is_auto", "created_at",
                    "n1", "n2", "n3", "n4", "n5", "n6")
    list_filter = ("round", "is_auto")
    search_fields = ("buyer_name",)
