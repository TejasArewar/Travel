from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.hashers import check_password
from django.http import JsonResponse
from django.db import models
from django.db.models import Sum
from .models import User, Expenses, Location, AmountReceived

def login_view(request):
    if request.session.get('user_id'):
        return redirect('home')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        try:
            user = User.objects.get(username=username)
            if check_password(password, user.password):
                request.session['user_id'] = user.id
                request.session['username'] = user.username
                request.session['name'] = user.name
                request.session['profile'] = user.profile
                return redirect('home')
            else:
                return render(request, 'login.html', {'error': 'Invalid credentials'})
        except User.DoesNotExist:
            return render(request, 'login.html', {'error': 'Invalid credentials'})
    
    return render(request, 'login.html')


def home(request):
    if not request.session.get('user_id'):
        return redirect('login')
    
    user = User.objects.get(id=request.session.get('user_id'))
    expenses = Expenses.objects.all().order_by('-inserted_on')
    itineraries = Location.objects.filter(user=user).order_by('-updated_on')
    
    # Calculate available amount from all users
    total_received = AmountReceived.objects.all().aggregate(
        total=Sum('amount_sent')
    )['total'] or 0
    
    total_spent = expenses.aggregate(total=Sum('amount_spent'))['total'] or 0
    available_amount = total_received - total_spent
    
    context = {
        'username': request.session.get('username'),
        'name': request.session.get('name'),
        'profile': request.session.get('profile'),
        'expenses': expenses,
        'itineraries': itineraries,
        'available_amount': available_amount,
        'total_received': total_received,
        'total_spent': total_spent
    }
    return render(request, 'home.html', context)


def add_expense(request):
    if not request.session.get('user_id'):
        return JsonResponse({'success': False, 'error': 'Not authenticated'})
    
    if request.session.get('profile') != 'Admin':
        return JsonResponse({'success': False, 'error': 'Not authorized'})
    
    if request.method == 'POST':
        spent_on = request.POST.get('spent_on')
        amount_spent = request.POST.get('amount_spent')
        
        expense = Expenses.objects.create(
            spent_on=spent_on,
            amount_spent=amount_spent
        )
        
        # Calculate updated available amount from all users
        total_received = AmountReceived.objects.all().aggregate(
            total=Sum('amount_sent')
        )['total'] or 0
        
        total_spent = Expenses.objects.aggregate(total=Sum('amount_spent'))['total'] or 0
        available_amount = total_received - total_spent
        
        return JsonResponse({
            'success': True,
            'expense': {
                'id': expense.id,
                'spent_on': expense.spent_on,
                'amount_spent': str(expense.amount_spent),
                'inserted_on': expense.inserted_on.strftime('%d %b %Y')
            },
            'available_amount': str(available_amount)
        })
    
    return JsonResponse({'success': False, 'error': 'Invalid request'})


def edit_expense(request, expense_id):
    if not request.session.get('user_id'):
        return JsonResponse({'success': False, 'error': 'Not authenticated'})
    
    if request.session.get('profile') != 'Admin':
        return JsonResponse({'success': False, 'error': 'Not authorized'})
    
    expense = get_object_or_404(Expenses, id=expense_id)
    
    if request.method == 'POST':
        expense.spent_on = request.POST.get('spent_on')
        expense.amount_spent = request.POST.get('amount_spent')
        expense.save()
        
        # Calculate updated available amount from all users
        total_received = AmountReceived.objects.all().aggregate(
            total=Sum('amount_sent')
        )['total'] or 0
        
        total_spent = Expenses.objects.aggregate(total=Sum('amount_spent'))['total'] or 0
        available_amount = total_received - total_spent
        
        return JsonResponse({
            'success': True,
            'expense': {
                'id': expense.id,
                'spent_on': expense.spent_on,
                'amount_spent': str(expense.amount_spent),
                'inserted_on': expense.inserted_on.strftime('%d %b %Y')
            },
            'available_amount': str(available_amount)
        })
    
    # GET request - return expense data
    return JsonResponse({
        'success': True,
        'expense': {
            'id': expense.id,
            'spent_on': expense.spent_on,
            'amount_spent': str(expense.amount_spent)
        }
    })


def delete_expense(request, expense_id):
    if not request.session.get('user_id'):
        return JsonResponse({'success': False, 'error': 'Not authenticated'})
    
    if request.session.get('profile') != 'Admin':
        return JsonResponse({'success': False, 'error': 'Not authorized'})
    
    expense = get_object_or_404(Expenses, id=expense_id)
    expense.delete()
    
    # Calculate updated available amount from all users
    total_received = AmountReceived.objects.all().aggregate(
        total=Sum('amount_sent')
    )['total'] or 0
    
    total_spent = Expenses.objects.aggregate(total=Sum('amount_spent'))['total'] or 0
    available_amount = total_received - total_spent
    
    return JsonResponse({
        'success': True,
        'available_amount': str(available_amount)
    })


def logout_view(request):
    request.session.flush()
    return redirect('login')


def add_location(request):
    if not request.session.get('user_id'):
        return JsonResponse({'success': False, 'error': 'Not authenticated'})
    
    if request.method == 'POST':
        user = User.objects.get(id=request.session.get('user_id'))
        itinerary_id = request.POST.get('itinerary_id')
        place_name = request.POST.get('place_name')
        latitude = request.POST.get('latitude')
        longitude = request.POST.get('longitude')
        address = request.POST.get('address', '')
        
        itinerary = get_object_or_404(Location, id=itinerary_id, user=user)
        
        # Add place to the itinerary
        place = {
            'name': place_name,
            'latitude': float(latitude),
            'longitude': float(longitude),
            'address': address
        }
        
        itinerary.place_data.append(place)
        itinerary.save()
        
        return JsonResponse({
            'success': True,
            'itinerary': {
                'id': itinerary.id,
                'itinerary_name': itinerary.itinerary_name,
                'places': itinerary.place_data
            }
        })
    
    return JsonResponse({'success': False, 'error': 'Invalid request'})


def create_itinerary(request):
    if not request.session.get('user_id'):
        return JsonResponse({'success': False, 'error': 'Not authenticated'})
    
    if request.method == 'POST':
        user = User.objects.get(id=request.session.get('user_id'))
        itinerary_name = request.POST.get('itinerary_name')
        
        itinerary = Location.objects.create(
            user=user,
            itinerary_name=itinerary_name,
            place_data=[]
        )
        
        return JsonResponse({
            'success': True,
            'itinerary': {
                'id': itinerary.id,
                'itinerary_name': itinerary.itinerary_name,
                'places': []
            }
        })
    
    return JsonResponse({'success': False, 'error': 'Invalid request'})


def delete_itinerary(request, itinerary_id):
    if not request.session.get('user_id'):
        return JsonResponse({'success': False, 'error': 'Not authenticated'})
    
    user = User.objects.get(id=request.session.get('user_id'))
    itinerary = get_object_or_404(Location, id=itinerary_id, user=user)
    itinerary.delete()
    
    return JsonResponse({'success': True})


def delete_place(request, itinerary_id, place_index):
    if not request.session.get('user_id'):
        return JsonResponse({'success': False, 'error': 'Not authenticated'})
    
    user = User.objects.get(id=request.session.get('user_id'))
    itinerary = get_object_or_404(Location, id=itinerary_id, user=user)
    
    if 0 <= place_index < len(itinerary.place_data):
        itinerary.place_data.pop(place_index)
        itinerary.save()
        return JsonResponse({'success': True, 'places': itinerary.place_data})
    
    return JsonResponse({'success': False, 'error': 'Invalid place index'})


def delete_location(request, location_id):
    # Kept for backward compatibility, redirects to delete_itinerary
    return delete_itinerary(request, location_id)


def get_locations(request):
    if not request.session.get('user_id'):
        return JsonResponse({'success': False, 'error': 'Not authenticated'})
    
    user = User.objects.get(id=request.session.get('user_id'))
    itineraries = Location.objects.filter(user=user).order_by('-updated_on')
    
    itineraries_data = [{
        'id': itin.id,
        'itinerary_name': itin.itinerary_name,
        'places': itin.place_data,
        'place_count': len(itin.place_data)
    } for itin in itineraries]
    
    return JsonResponse({'success': True, 'itineraries': itineraries_data})


def get_itinerary(request, itinerary_id):
    if not request.session.get('user_id'):
        return JsonResponse({'success': False, 'error': 'Not authenticated'})
    
    current_user = User.objects.get(id=request.session.get('user_id'))
    itinerary = get_object_or_404(Location, id=itinerary_id)
    
    # Check if user owns this itinerary
    is_owner = itinerary.user.id == current_user.id
    
    return JsonResponse({
        'success': True,
        'itinerary': {
            'id': itinerary.id,
            'itinerary_name': itinerary.itinerary_name,
            'places': itinerary.place_data,
            'owner': itinerary.user.name,
            'is_owner': is_owner
        }
    })


def get_all_users(request):
    if not request.session.get('user_id'):
        return JsonResponse({'success': False, 'error': 'Not authenticated'})
    
    current_user_id = request.session.get('user_id')
    users = User.objects.exclude(id=current_user_id).values('id', 'name', 'username')
    
    return JsonResponse({
        'success': True,
        'users': list(users)
    })


def get_user_itineraries(request, user_id):
    if not request.session.get('user_id'):
        return JsonResponse({'success': False, 'error': 'Not authenticated'})
    
    user = get_object_or_404(User, id=user_id)
    itineraries = Location.objects.filter(user=user).order_by('-updated_on')
    
    itineraries_data = [{
        'id': itin.id,
        'itinerary_name': itin.itinerary_name,
        'places': itin.place_data,
        'place_count': len(itin.place_data),
        'owner': user.name
    } for itin in itineraries]
    
    return JsonResponse({
        'success': True,
        'itineraries': itineraries_data,
        'user_name': user.name
    })