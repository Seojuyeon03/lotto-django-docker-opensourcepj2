from django.db import models
from django.utils import timezone

class LottoRound(models.Model):
    round_no = models.IntegerField(unique=True, verbose_name="회차")
    draw_date = models.DateTimeField(default=timezone.now, verbose_name="추첨일")

    # 당첨 번호 (처음에는 비워두고, 추첨 후 채움)
    n1 = models.IntegerField(null=True, blank=True)
    n2 = models.IntegerField(null=True, blank=True)
    n3 = models.IntegerField(null=True, blank=True)
    n4 = models.IntegerField(null=True, blank=True)
    n5 = models.IntegerField(null=True, blank=True)
    n6 = models.IntegerField(null=True, blank=True)
    bonus = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return f"{self.round_no}회"

    def is_drawn(self):
        return self.n1 is not None


class LottoTicket(models.Model):
    round = models.ForeignKey(LottoRound, on_delete=models.CASCADE, verbose_name="회차")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="구매 시간")
    buyer_name = models.CharField(max_length=50, blank=True, verbose_name="구매자 이름")
    is_auto = models.BooleanField(default=False, verbose_name="자동 여부")

    n1 = models.IntegerField()
    n2 = models.IntegerField()
    n3 = models.IntegerField()
    n4 = models.IntegerField()
    n5 = models.IntegerField()
    n6 = models.IntegerField()

    def __str__(self):
        return f"{self.round.round_no}회 {self.buyer_name or '익명'}"

    def numbers(self):
        return [self.n1, self.n2, self.n3, self.n4, self.n5, self.n6]
