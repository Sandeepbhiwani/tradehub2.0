from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from assets.utils import place_order
from stockmanagement.models import Stock
from django.contrib import messages
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q, Sum, Case, When, IntegerField
from django.utils import timezone
from datetime import timedelta
from .models import order as Order
from .models import Position
from decimal import Decimal
import json
from django.core.serializers.json import DjangoJSONEncoder

@login_required
def orders_view(request):
    # Get filter parameters
    status_filter = request.GET.get('status', 'all')
    order_type_filter = request.GET.get('type', 'all')
    time_filter = request.GET.get('time', 'all')
    search_query = request.GET.get('search', '')
    page_number = request.GET.get('page', 1)
    
    # Base queryset
    orders = Order.objects.filter(user=request.user).select_related('stock')
    
    # Apply filters
    if status_filter != 'all':
        orders = orders.filter(status=status_filter)
    
    if order_type_filter != 'all':
        orders = orders.filter(order_type=order_type_filter)
    
    if search_query:
        orders = orders.filter(
            Q(stock__symbol__icontains=search_query) |
            Q(stock__name__icontains=search_query)
        )
    
    # Time-based filtering
    now = timezone.now()
    if time_filter == 'today':
        today = now.date()
        orders = orders.filter(created_at__date=today)
    elif time_filter == 'week':
        week_ago = now - timedelta(days=7)
        orders = orders.filter(created_at__gte=week_ago)
    elif time_filter == 'month':
        month_ago = now - timedelta(days=30)
        orders = orders.filter(created_at__gte=month_ago)
    
    # Order by creation date (most recent first)
    orders = orders.order_by('-created_at')
    
    # Pagination
    paginator = Paginator(orders, 10)  # 10 orders per page for mobile
    try:
        orders_page = paginator.page(page_number)
    except PageNotAnInteger:
        orders_page = paginator.page(1)
    except EmptyPage:
        orders_page = paginator.page(paginator.num_pages)
    
    # Statistics
    total_orders = Order.objects.filter(user=request.user).count()
    total_investment = Order.objects.filter(
        user=request.user, 
        status='completed',
        order_type='BUY'
    ).aggregate(total=Sum('amount'))['total'] or 0
    
    context = {
        'orders': orders_page,
        'status_filter': status_filter,
        'order_type_filter': order_type_filter,
        'time_filter': time_filter,
        'search_query': search_query,
        'total_orders': total_orders,
        'total_investment': total_investment,
        'page_range': paginator.get_elided_page_range(number=orders_page.number, on_each_side=1, on_ends=1)
    }
    
    return render(request, 'dashboard/orders.html', context)


@login_required
def initiate_order(request):
    if request.method == 'POST':
        symbol = request.POST.get("symbol")
        quantity = int(request.POST.get("quantity"))
        order_type = request.POST.get("order_type")
        # if not market_open(segment):
        #     messages.error(request,'Market is closed.')
        #     return redirect('/orders')
        stock = Stock.objects.filter(symbol=symbol).first()
        status, response = place_order(request.user, stock, quantity , order_type)
        if status:
            messages.success(request, response)
        else:
            messages.error(request, response)
        return redirect('orders')
    else:
        return redirect('watchlist')
    

@login_required
def portfolio_view(request):
    # Get all positions for the current user
    positions = Position.objects.filter(user=request.user).select_related('stock')
    
    # Calculate portfolio metrics
    open_positions = positions.filter(is_closed=False)
    closed_positions = positions.filter(is_closed=True)
    
    labels = [pos.stock.name for pos in open_positions]
    data = [pos.quantity * pos.buy_price for pos in open_positions]  # investment value per stock

    chart_data = {
        'labels': labels,
        'data': data,
    }

    chart_data_json = json.dumps(chart_data, cls=DjangoJSONEncoder)


    # Calculate total portfolio value and P&L
    total_investment = sum(position.quantity * position.buy_price for position in open_positions)
    current_value = 0
    total_unrealised_pnl = current_value - total_investment
    total_realised_pnl = sum(position.realised_pnl for position in closed_positions)
    
    # Calculate today's P&L (positions traded today)
    today = timezone.now().date()
    today_positions = positions.filter(last_traded_datetime__date=today)
    today_pnl = sum(position.realised_pnl for position in today_positions)
    current_value = 0

    # Group positions by stock for summary
    position_summary = {}
    for position in open_positions:
        stock_symbol = position.stock.symbol
        if stock_symbol not in position_summary:
            position_summary[stock_symbol] = {
                'stock': position.stock,
                'total_quantity': position.quantity,
                'avg_buy_price': position.buy_price,
                'total_investment': position.buy_price * position.quantity,
                'current_value': Decimal(position.quantity) * Decimal(position.stock.current_price),
                'unrealised_pnl': Decimal((position.quantity*position.stock.current_price))-Decimal((position.buy_price*position.quantity)),
            }
        
    
    # Calculate average buy price and P&L for each stock
    for symbol, summary in position_summary.items():
        summary['pnl_percentage'] = (Decimal(summary['unrealised_pnl']) / Decimal(summary['total_investment']) * 100) if summary['total_investment'] > 0 else 0
        current_value += summary['current_value']
    
    context = {
        'positions': positions,
        'open_positions': open_positions,
        'closed_positions': closed_positions,
        'position_summary': position_summary,
        'total_investment': total_investment,
        'current_value': current_value,
        'total_unrealised_pnl': total_unrealised_pnl,
        'total_realised_pnl': total_realised_pnl,
        'today_pnl': today_pnl,
        'total_positions': positions.count(),
        'open_positions_count': open_positions.count(),
        'closed_positions_count': closed_positions.count(),
        'chart_data_json': chart_data_json,
        'chart_data': chart_data,
    }
    
    return render(request, 'dashboard/portfolio.html', context)