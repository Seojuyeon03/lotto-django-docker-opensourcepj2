from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.contrib.admin.views.decorators import staff_member_required
import random

from .models import LottoRound, LottoTicket


def index(request):
    context = {
        "title": "로또 웹페이지"
    }
    return render(request, "lotto_app/index.html", context)

def get_current_round():
    """
    현재 판매 중인 회차를 가져오는 헬퍼 함수.
    - 기존 회차가 하나도 없으면 1회차를 새로 만든다.
    - 있으면 가장 큰 회차를 '현재 회차'라고 본다.
    """
    latest_round = LottoRound.objects.order_by("-round_no").first()
    if latest_round is None:
        # 회차가 없으면 1회차 생성
        latest_round = LottoRound.objects.create(
            round_no=1,
            draw_date=timezone.now()
        )
    return latest_round


def buy_ticket(request):
    """
    로또 구매 페이지 (수동/자동)
    """
    if request.method == "POST":
        buyer_name = request.POST.get("buyer_name", "").strip()
        mode = request.POST.get("mode", "auto")  # 기본값 자동

        current_round = get_current_round()

        # 자동 모드: 랜덤 번호 6개 생성
        if mode == "auto":
            numbers = random.sample(range(1, 46), 6)
        else:
            # 수동 모드: 사용자 입력 값 가져오기
            nums_str = [
                request.POST.get("n1"),
                request.POST.get("n2"),
                request.POST.get("n3"),
                request.POST.get("n4"),
                request.POST.get("n5"),
                request.POST.get("n6"),
            ]

            # 간단한 유효성 검사 (정수 변환 + 중복 제거 + 범위 체크)
            try:
                numbers = [int(x) for x in nums_str]
            except (TypeError, ValueError):
                return render(request, "lotto_app/buy_ticket.html", {
                    "error": "모든 번호를 올바른 숫자로 입력해 주세요.",
                })

            if len(set(numbers)) != 6:
                return render(request, "lotto_app/buy_ticket.html", {
                    "error": "번호는 서로 다른 6개여야 합니다.",
                })

            if not all(1 <= x <= 45 for x in numbers):
                return render(request, "lotto_app/buy_ticket.html", {
                    "error": "번호는 1부터 45 사이여야 합니다.",
                })

        # LottoTicket 객체 저장
        ticket = LottoTicket.objects.create(
            round=current_round,
            buyer_name=buyer_name,
            is_auto=(mode == "auto"),
            n1=numbers[0],
            n2=numbers[1],
            n3=numbers[2],
            n4=numbers[3],
            n5=numbers[4],
            n6=numbers[5],
        )

        return render(request, "lotto_app/buy_complete.html", {
            "ticket": ticket,
            "numbers": numbers,
            "round": current_round,
        })

    # GET 요청일 때 (처음 페이지 열었을 때)
    return render(request, "lotto_app/buy_ticket.html")


def my_tickets(request):
    """
    최근 구매된 로또 티켓 목록 확인 페이지
    (로그인 기능은 없으므로, 일단 전체 티켓 중 최신 몇 개만 보여주기)
    """
    tickets = LottoTicket.objects.order_by("-created_at")[:20]
    return render(request, "lotto_app/my_tickets.html", {
        "tickets": tickets,
    })

def calc_rank(round_obj, numbers):
    """
    round_obj: LottoRound 인스턴스
    numbers: 사용자가 선택한 번호 리스트 (길이 6)
    return: (rank, match_count, bonus_match)
        rank: 1~5등, 꽝이면 0
    """
    # 당첨 번호/보너스가 아직 안 정해졌으면 꽝 처리
    if not round_obj.is_drawn() or round_obj.bonus is None:
        return 0, 0, False

    winning = [
        round_obj.n1,
        round_obj.n2,
        round_obj.n3,
        round_obj.n4,
        round_obj.n5,
        round_obj.n6,
    ]
    bonus = round_obj.bonus

    match_count = len(set(winning) & set(numbers))
    bonus_match = bonus in numbers

    # 로또 기본 규칙 적용
    if match_count == 6:
        rank = 1
    elif match_count == 5 and bonus_match:
        rank = 2
    elif match_count == 5:
        rank = 3
    elif match_count == 4:
        rank = 4
    elif match_count == 3:
        rank = 5
    else:
        rank = 0

    return rank, match_count, bonus_match


def check_result(request):
    """
    사용자가 회차 + 번호 6개를 입력하면 몇 등인지 알려주는 페이지
    """
    context = {}

    if request.method == "POST":
        round_no = request.POST.get("round_no")
        nums_str = [
            request.POST.get("n1"),
            request.POST.get("n2"),
            request.POST.get("n3"),
            request.POST.get("n4"),
            request.POST.get("n5"),
            request.POST.get("n6"),
        ]

        # 회차 번호 유효성 검사
        try:
            round_no_int = int(round_no)
        except (TypeError, ValueError):
            context["error"] = "회차 번호를 올바르게 입력해 주세요."
            return render(request, "lotto_app/check_result.html", context)

        round_obj = LottoRound.objects.filter(round_no=round_no_int).first()
        if round_obj is None:
            context["error"] = f"{round_no_int}회 정보가 없습니다. 먼저 회차를 생성해 주세요."
            return render(request, "lotto_app/check_result.html", context)

        # 번호 유효성 검사
        try:
            numbers = [int(x) for x in nums_str]
        except (TypeError, ValueError):
            context["error"] = "모든 번호를 올바른 숫자로 입력해 주세요."
            return render(request, "lotto_app/check_result.html", context)

        if len(set(numbers)) != 6:
            context["error"] = "번호는 서로 다른 6개여야 합니다."
            return render(request, "lotto_app/check_result.html", context)

        if not all(1 <= x <= 45 for x in numbers):
            context["error"] = "번호는 1부터 45 사이여야 합니다."
            return render(request, "lotto_app/check_result.html", context)

        # 등수 계산
        rank, match_count, bonus_match = calc_rank(round_obj, numbers)

        rank_text_map = {
            1: "1등",
            2: "2등",
            3: "3등",
            4: "4등",
            5: "5등",
            0: "낙첨",
        }

        context.update({
            "round": round_obj,
            "numbers": numbers,
            "rank": rank,
            "rank_text": rank_text_map.get(rank, "낙첨"),
            "match_count": match_count,
            "bonus_match": bonus_match,
        })

    return render(request, "lotto_app/check_result.html", context)


@staff_member_required
def admin_round_list(request):
    """
    관리자용: 회차 목록 페이지
    (회차는 /admin 에서 추가해도 되고, 여기서는 조회 위주)
    """
    rounds = LottoRound.objects.order_by("-round_no")
    return render(request, "lotto_app/admin_round_list.html", {
        "rounds": rounds,
    })


@staff_member_required
def admin_draw_round(request, round_no):
    """
    관리자용: 특정 회차의 당첨 번호 추첨
    """
    round_obj = get_object_or_404(LottoRound, round_no=round_no)

    if not round_obj.is_drawn():
        nums = random.sample(range(1, 46), 7)
        round_obj.n1 = nums[0]
        round_obj.n2 = nums[1]
        round_obj.n3 = nums[2]
        round_obj.n4 = nums[3]
        round_obj.n5 = nums[4]
        round_obj.n6 = nums[5]
        round_obj.bonus = nums[6]
        round_obj.save()

    return redirect("lotto_app:admin_round_detail", round_no=round_no)


@staff_member_required
def admin_round_detail(request, round_no):
    """
    관리자용: 특정 회차 상세 + 당첨자 목록
    """
    round_obj = get_object_or_404(LottoRound, round_no=round_no)
    tickets = LottoTicket.objects.filter(round=round_obj).order_by("-created_at")

    winners = []
    for t in tickets:
        numbers = t.numbers()
        rank, match_count, bonus_match = calc_rank(round_obj, numbers)
        if rank > 0:
            winners.append({
                "ticket": t,
                "numbers": numbers,
                "rank": rank,
                "match_count": match_count,
                "bonus_match": bonus_match,
            })

    # 등수 순으로 정렬 (1등 우선)
    winners.sort(key=lambda x: x["rank"])

    return render(request, "lotto_app/admin_round_detail.html", {
        "round": round_obj,
        "tickets": tickets,
        "winners": winners,
    })


# Create your views here.
