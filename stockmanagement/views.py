# # from django.contrib.auth.decorators import login_required
# # from django.shortcuts import render
# # from django.db.models import Sum, Count, Q, F
# # from decimal import Decimal
# # import json
# # from datetime import datetime
# # from assets.models import Position
# # from stockmanagement.models import Stock
# # from django.core.serializers.json import DjangoJSONEncoder

# # @login_required(login_url='login')
# # def watchlist(request):
# #     stocks = Stock.objects.all().order_by('symbol')

# #     context = {
# #         'stocks': stocks,
# #     }
# #     return render(request, "stockmanagement/watchlist.html", context)
# #     # return render(request, "test.html", context)
# from django.contrib.auth.decorators import login_required
# from django.shortcuts import render
# from django.db.models import Sum, Count, Q, F
# from decimal import Decimal
# import json
# from datetime import datetime
# from assets.models import Position
# from stockmanagement.models import Stock
# from django.core.serializers.json import DjangoJSONEncoder

# # NEW
# from django.utils import timezone
# from zoneinfo import ZoneInfo      # Python 3.9+

# IST = ZoneInfo("Asia/Kolkata")


# @login_required(login_url='login')
# def watchlist(request):
#     # get current time in Indian timezone
#     ist_now = timezone.now().astimezone(IST)

#     # fetch stocks and override last_updated just for rendering
#     stocks = list(Stock.objects.all().order_by('symbol'))
#     for stock in stocks:
#         stock.last_updated = ist_now   # not saved to DB, only in memory

#     context = {
#         'stocks': stocks,
#     }
#     return render(request, "stockmanagement/watchlist.html", context)

from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.db.models import Sum, Count, Q, F
from decimal import Decimal
import json
from datetime import datetime,timedelta
from assets.models import Position
from stockmanagement.models import Stock
from django.core.serializers.json import DjangoJSONEncoder

# NEW: use zoneinfo for Asia/Kolkata
from zoneinfo import ZoneInfo

IST = ZoneInfo("Asia/Kolkata")


@login_required(login_url='login')
def watchlist(request):
    # current time in Indian Standard Time (IST)
    # ist_now = datetime.now(IST)
    ist_now = datetime.now(IST) + timedelta(hours=5, minutes=30)
    # fetch stocks and override last_updated just for display
    stocks = list(Stock.objects.all().order_by('symbol'))
    for stock in stocks:
        stock.last_updated = ist_now   # not saved to DB, only in memory

    context = {
        'stocks': stocks,
    }
    return render(request, "stockmanagement/watchlist.html", context)
