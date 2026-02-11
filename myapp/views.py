from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.response import Response
from rest_framework import authentication, permissions
from django.db.models import Sum
from .models import User, Income, Expense
from rest_framework import status
from rest_framework.authtoken.models import Token 
from rest_framework.permissions import IsAuthenticated
from datetime import datetime
from decimal import Decimal


# Create your views here.


@api_view(['POST'])
def register_user(request):
    """
    Register a new user.
    Expected JSON body:
    {
        "name": "John Doe",
        "email": "john@example.com",
        "password": "securepassword"
    }
    """

    data = request.data
    name = data.get('name')
    email = data.get('email')
    password = data.get('password')

    if not all([name, email, password]):
        return Response({"error": "Name, email and password are required."},
                        status=status.HTTP_400_BAD_REQUEST)
    
    if User.objects.filter(email = email).exists():
        return Response({"error": "Email is already registered."},
                        status=status.HTTP_400_BAD_REQUEST)
    
    user = User.objects.create_user(name=name, email=email, password=password)

    token, _ = Token.objects.get_or_create(user=user)

    return Response({
        "message": "User registered successfully.",
        "user": {
            "id": user.id,
            "name": user.name,
            "email": user.email
        },
        "token": token.key
    }, status=status.HTTP_201_CREATED)



@api_view(['POST', 'GET'])
@permission_classes([IsAuthenticated])
def income_list_create(request):
    user = request.user

    if request.method == 'POST':
        data = request.data
        amount = data.get('amount')
        inc_category = data.get('inc_category')
        description = data.get('description', '')
        date = data.get('date')
        is_recurring = data.get('is_recurring', False)

        # Validation
        if not all([amount, inc_category, date]):
            return Response(
                {"error": "amount, inc_category, and date are required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Create income
        income = Income.objects.create(
            user=user,
            amount=amount,
            inc_category=inc_category,
            description=description,
            date=date,
            is_recurring=is_recurring
        )

        return Response({
            "message": "Income added successfully.",
            "income": {
                "id": income.id,
                "amount": str(income.amount),
                "category": income.get_inc_category_display(),
                "description": income.description,
                "date": income.date,
                "is_recurring": income.is_recurring
            }
        }, status=status.HTTP_201_CREATED)

    # GET method: list all incomes for the user
    elif request.method == 'GET':
        incomes = Income.objects.filter(user=user).order_by('-date')
        income_list = [{
            "id": i.id,
            "amount": str(i.amount),
            "category": i.get_inc_category_display(),
            "description": i.description,
            "date": i.date,
            "is_recurring": i.is_recurring
        } for i in incomes]

        return Response(income_list, status=status.HTTP_200_OK)
    
@api_view(['POST', 'GET'])
@permission_classes([IsAuthenticated])
def expense_list_create(request):
    user = request.user

    if request.method == 'POST':
        data = request.data
        amount = data.get('amount')
        exp_category = data.get('exp_category')
        description = data.get('description', '')
        date = data.get('date')
        is_recurring =data.get('is_recurring', False)

        if not all([amount, exp_category, date]):
            return Response(
                {"error": "amount, exp_category, and date are required."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        expense = Expense.objects.create(
            user = user,
            amount= amount,
            exp_category = exp_category,
            description = description,
            date = date,
            is_recurring = is_recurring
        )

        return Response({
            "message": "Expense added successfully.",
            "expence": {
                "id" : expense.id,
                "amount" : str(expense.amount),
                "category" : expense.get_exp_category_display(),
                "description": expense.description,
                "date" : expense.date,
                "is_recurring": expense.is_recurring
            }
        }, status=status.HTTP_201_CREATED)
    
    elif request.method == 'GET':
        expenses = Expense.objects.filter(user=user).order_by('-date')
        expence_list = [{
            "id": i.id,
            "amount": str(i.amount),
            "category": i.get_exp_category_display(),
            "description": i.description,
            "date": i.date,
            "is_recurring": i.is_recurring
        } for i in expenses]

        return Response(expence_list, status = status.HTTP_200_OK)
    

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def budget_view(request):
    user = request.user

    # Get month and year from query params, default to current month
    month = int(request.GET.get('month', datetime.now().month))
    year = int(request.GET.get('year', datetime.now().year))

    # Sum all incomes for the month
    total_income = Income.objects.filter(
        user=user,
        date__year=year,
        date__month=month
    ).aggregate(total=Sum('amount'))['total'] or 0

    # Sum all expenses for the month
    total_expense = Expense.objects.filter(
        user=user,
        date__year=year,
        date__month=month
    ).aggregate(total=Sum('amount'))['total'] or 0

    recommended_spending = (total_income * Decimal('0.6')).quantize(Decimal('0.01'))
    recommended_saving = (total_income * Decimal('0.2')).quantize(Decimal('0.01'))

    # Calculate remaining after expenses
    remaining = round(total_income - total_expense, 2)

    return Response({
        "month": month,
        "year": year,
        "total_income": str(total_income),
        "total_expense": str(total_expense),
        "recommended_spending": str(recommended_spending),
        "recommended_saving": str(recommended_saving),
        "remaining_balance": str(remaining)
    }, status=status.HTTP_200_OK)