from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.db.models import Sum
from .models import User, Income, Expense
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from datetime import datetime
from decimal import Decimal


# Create your views here.


@api_view(['POST'])
def register_user(request):

    data = request.data
    name = data.get('name')
    email = data.get('email')
    password = data.get('password')

    if not all([name, email, password]):
        return Response(
            {"error": "Name, email and password are required."},
            status=status.HTTP_400_BAD_REQUEST
        )

    if User.objects.filter(email=email).exists():
        return Response(
            {"error": "Email is already registered."},
            status=status.HTTP_400_BAD_REQUEST
        )

    user = User.objects.create_user(
        email=email,
        password=password,
        name=name
    )

    return Response({
        "message": "User registered successfully.",
        "user": {
            "id": user.id,
            "name": user.name,
            "email": user.email
        }
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
    
@api_view(['PUT', 'PATCH', 'DELETE'])
@permission_classes([IsAuthenticated])
def income_detail(request, pk):
    user = request.user

    try:
        income = Income.objects.get(pk=pk, user=user)
    except Income.DoesNotExist:
        return Response(
            {"error": "Income not found."},
            status=status.HTTP_404_NOT_FOUND
        )

    # UPDATE (Full update)
    if request.method == 'PUT':
        data = request.data
        income.amount = data.get('amount', income.amount)
        income.inc_category = data.get('inc_category', income.inc_category)
        income.description = data.get('description', income.description)
        income.date = data.get('date', income.date)
        income.is_recurring = data.get('is_recurring', income.is_recurring)
        income.save()

        return Response({"message": "Income updated successfully."})

    # PARTIAL UPDATE
    elif request.method == 'PATCH':
        data = request.data

        for field in ['amount', 'inc_category', 'description', 'date', 'is_recurring']:
            if field in data:
                setattr(income, field, data[field])

        income.save()
        return Response({"message": "Income partially updated successfully."})

    # DELETE
    elif request.method == 'DELETE':
        income.delete()
        return Response({"message": "Income deleted successfully."},
                        status=status.HTTP_204_NO_CONTENT)
    
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
            "expense": {
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
        expense_list = [{
            "id": i.id,
            "amount": str(i.amount),
            "category": i.get_exp_category_display(),
            "description": i.description,
            "date": i.date,
            "is_recurring": i.is_recurring
        } for i in expenses]

        return Response(expense_list, status = status.HTTP_200_OK)
    
@api_view(['PUT', 'PATCH', 'DELETE'])
@permission_classes([IsAuthenticated])
def expense_detail(request, pk):
    user = request.user

    try:
        expense = Expense.objects.get(pk=pk, user=user)
    except Expense.DoesNotExist:
        return Response(
            {"error": "Expense not found."},
            status=status.HTTP_404_NOT_FOUND
        )

    if request.method == 'PUT':
        data = request.data
        expense.amount = data.get('amount', expense.amount)
        expense.exp_category = data.get('exp_category', expense.exp_category)
        expense.description = data.get('description', expense.description)
        expense.date = data.get('date', expense.date)
        expense.is_recurring = data.get('is_recurring', expense.is_recurring)
        expense.save()

        return Response({"message": "Expense updated successfully."})

    elif request.method == 'PATCH':
        data = request.data

        for field in ['amount', 'exp_category', 'description', 'date', 'is_recurring']:
            if field in data:
                setattr(expense, field, data[field])

        expense.save()
        return Response({"message": "Expense partially updated successfully."})

    elif request.method == 'DELETE':
        expense.delete()
        return Response({"message": "Expense deleted successfully."},
                        status=status.HTTP_204_NO_CONTENT)
    
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def budget_view(request):
    user = request.user

    # Sum all incomes for the user
    total_income = Income.objects.filter(
        user=user
    ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')

    # Sum all expenses for the user
    total_expense = Expense.objects.filter(
        user=user
    ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')

    recommended_spending = (total_income * Decimal('0.6')).quantize(Decimal('0.01'))
    recommended_saving = (total_income * Decimal('0.2')).quantize(Decimal('0.01'))

    remaining = (total_income - total_expense).quantize(Decimal('0.01'))

    return Response({
        "total_income": str(total_income),
        "total_expense": str(total_expense),
        "recommended_spending": str(recommended_spending),
        "recommended_saving": str(recommended_saving),
        "remaining_balance": str(remaining)
    }, status=status.HTTP_200_OK)