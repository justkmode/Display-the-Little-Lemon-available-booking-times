from django.shortcuts import render
from .forms import BookingForm
from .models import Menu
from .models import Booking
from django.core import serializers
from datetime import datetime
import json
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, JsonResponse

# Home view
def home(request):
    return render(request, 'index.html')

# About view
def about(request):
    return render(request, 'about.html')

# Reservations view (displays all bookings for a specific date and passes JSON data to template)
def reservations(request):
    date = request.GET.get('date', datetime.today().strftime('%Y-%m-%d'))  # Ensure date is in YYYY-MM-DD format
    bookings = Booking.objects.filter(reservation_date=date)  # Filter by date
    booking_json = serializers.serialize('json', bookings)  # Convert to JSON

    # Pass both the raw and formatted data to the template
    return render(request, 'bookings.html', {
        "formatted_bookings": bookings,  # Pass queryset for formatting in the template
        "raw_json": booking_json,  # Pass raw JSON data
        "date": date,
        "today": datetime.today().strftime('%Y-%m-%d')  # Pass the current date in correct format
    })

# Book view (handles form submissions for booking)
def book(request):
    form = BookingForm()
    if request.method == 'POST':
        form = BookingForm(request.POST)
        if form.is_valid():
            form.save()
    context = {'form': form}
    return render(request, 'book.html', context)

# Menu view (displays all menu items)
def menu(request):
    menu_data = Menu.objects.all()
    main_data = {"menu": menu_data}
    return render(request, 'menu.html', {"menu": main_data})

# Display specific menu item
def display_menu_item(request, pk=None):
    if pk:
        menu_item = Menu.objects.get(pk=pk)
    else:
        menu_item = ""
    return render(request, 'menu_item.html', {"menu_item": menu_item})

# CSRF-exempt bookings view to handle new bookings and return JSON response
@csrf_exempt
def bookings(request):
    if request.method == 'POST':
        data = json.loads(request.body.decode('utf-8'))  # Decode JSON body
        exist = Booking.objects.filter(reservation_date=data['reservation_date']).filter(
            reservation_slot=data['reservation_slot']).exists()

        if not exist:
            booking = Booking(
                first_name=data['first_name'],
                reservation_date=data['reservation_date'],
                reservation_slot=data['reservation_slot'],
            )
            booking.save()
        else:
            return JsonResponse({'error': 1}, status=400)

    # If it's a GET request, show bookings for a specific date
    date = request.GET.get('date', datetime.today().strftime('%Y-%m-%d'))
    bookings = Booking.objects.filter(reservation_date=date)  # Filter by the date
    booking_json = serializers.serialize('json', bookings)

    return JsonResponse(json.loads(booking_json), safe=False)  # Return JSON directly
