from django.shortcuts import render,redirect, get_object_or_404
from django.contrib import messages
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from time import gmtime, strftime
from django.contrib.auth.models import User
from .models import Onwer, Hotel, Room
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout as auth_logout
from django.contrib.auth.decorators import user_passes_test
from django.core.files.storage import FileSystemStorage
from django.contrib.auth.hashers import make_password, check_password
from django.contrib.auth.forms import AuthenticationForm

def index(request):
    context= {
        "time": strftime("%d-%m-%Y %H:%M %p", gmtime())
    }
    return render(request, 'myApp/index.html', context)

def about1(request):
    return render(request,"myApp/about_us.html")

def about(request):
    if request.user.is_authenticated:
        try:
            onwer = Onwer.objects.get(email=request.user.email)
            if onwer.status == 'pending':
                messages.info(request, 'Your registration is pending approval from the admin.')
                return render(request, 'myApp/dashboard_owner.html')
            elif onwer.status == 'rejected':
                messages.error(request, 'Your registration was rejected. Please contact the admin.')
                return render(request, 'myApp/dashboard_owner.html')
            return render(request, 'myApp/dashboard_owner.html')
        except Onwer.DoesNotExist:
            return redirect('index')  
    else:
        return redirect('login')

def dashboard_user(request):
    if request.user.is_authenticated:
        name = request.user.first_name  
    else:
        name = 'Guest'  
    actions = ['available', 'checked']  
    context = {
        'name': name,
        'actions': actions,
    }
    return render(request, 'myApp/dashboard_user.html', context)

@login_required
def dashboard_owner(request):
    try:
        # Fetch hotels where the owner matches the logged-in user
        hotels = Hotel.objects.filter(owner=request.user)
        rooms = Room.objects.filter(hotel__in=hotels)

        if request.method == 'POST':
            hotel_name = request.POST.get('hotel_name')
            room_types = request.POST.getlist('room_type[]')
            room_counts = request.POST.getlist('room_count[]')
            facilities_list = request.POST.getlist('facilities[]')
            photos = request.FILES.getlist('photos[]')

            if not hotel_name:
                messages.error(request, "Hotel name is required.")
                return redirect('dashboard_owner')

            # Create or get the hotel with the logged-in user as the owner
            hotel, created = Hotel.objects.get_or_create(name=hotel_name, owner=request.user)

            # Add room types
            for i in range(len(room_types)):
                room_type = room_types[i]
                room_count = room_counts[i]
                facilities = facilities_list[i]
                photo = photos[i] if i < len(photos) else None

                Room.objects.create(
                    hotel=hotel,
                    room_type=room_type,
                    room_count=room_count,
                    facilities=facilities,
                    photos=photo
                )

            messages.success(request, "Rooms added successfully.")
            return redirect('dashboard_owner')

        context = {'rooms': rooms}
        return render(request, 'myApp/dashboard_owner.html', context)

    except Exception as e:
        messages.error(request, f"An error occurred: {e}")
        return redirect('owner_login')

def create_user(request):
    if request.method == "GET":
        return render(request, 'myApp/register_user.html')
    
    if request.method == "POST":
        name = request.POST.get('first_name')
        surname = request.POST.get('last_name')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confpass = request.POST.get('confpass')

        if not all([name, surname, email, password, confpass]):
            messages.error(request, "All fields are required.")
            return render(request, 'myApp/register_user.html')

        if len(name) < 3:
            messages.error(request, "First name must be at least 3 characters long.")
            return render(request, 'myApp/register_user.html')

        if len(surname) < 3:
            messages.error(request, "Last name must be at least 3 characters long.")
            return render(request, 'myApp/register_user.html')
        
        if len(password) < 8:
            messages.error(request, "Password must be at least 8 characters long.")
            return render(request, 'myApp/register_user.html')

        try:
            validate_email(email)
        except ValidationError:
            messages.error(request, "Invalid email address.")
            return render(request, 'myApp/register_user.html')

        if User.objects.filter(email=email).exists():
            messages.error(request, "Email is already registered.")
            return render(request, 'myApp/register_user.html')

        if password != confpass:
            messages.error(request, "Passwords do not match.")
            return render(request, 'myApp/register_user.html')
        
        # Create the user without using create_user
        try:
            user = User.objects.create(
                first_name=name,
                last_name=surname,
                email=email,
                password=make_password(password)  # Store hashed password
            )
            user.save()
            messages.success(request, "User registered successfully!")
            return redirect('/dashboard-user')

        except Exception as e:
            messages.error(request, f"An error occurred: {e}")
            return render(request, 'myApp/register_user.html')
        
def create_owner(request):
    if request.method == "GET":
        return render(request, 'myApp/register_owner.html')

    if request.method == "POST":
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        email = request.POST['email']
        password = request.POST['password']
        confpass = request.POST['confpass']
        certificate = request.FILES.get('certificate')

        # Validate required fields
        if not first_name or not last_name or not email or not password or not confpass or not certificate:
            messages.error(request, "All fields are required.")
            return redirect('owner')

        # Check if first name and last name have at least 3 characters
        if len(first_name) < 3 or len(last_name) < 3:
            messages.error(request, "First name and last name must be at least 3 characters long.")
            return redirect('owner')

        # Check if password and confirm password match
        if password != confpass:
            messages.error(request, "Passwords do not match.")
            return redirect('owner')

        # Validate email format
        try:
            validate_email(email)
        except ValidationError:
            messages.error(request, "Invalid email format.")
            return redirect('owner')

        # Check if email already exists in the database
        if Onwer.objects.filter(email=email).exists():
            messages.error(request, "An account with this email already exists.")
            return redirect('owner')

        # Validate file upload: Allow only one file
        if not certificate:
            messages.error(request, "Certificate is required.")
            return redirect('owner')
        
        # Ensure the uploaded file is a single file and not multiple files
        if isinstance(certificate, list):
            messages.error(request, "Please upload only one file.")
            return redirect('owner')

        # Save the owner if all validations pass
        hashed_password1 = make_password(password)
        owner = Onwer(
            first_name=first_name,
            last_name=last_name,
            email=email,
            password=hashed_password1, 
            certificate=certificate,
            status='pending'
        )
        owner.save()
        messages.success(request, 'You should wait for admin approval to continue with registration.')
        return redirect('index')
    
@user_passes_test(lambda user: user.is_superuser)  # Restrict this view to admin users
def manage_owners(request):
    # Get all owners with pending status
    pending_owners = Onwer.objects.filter(status='pending')
    context = {
        'pending_owners': pending_owners
    }
    return render(request, 'myApp/manage_owners.html', context)

# Admin view to approve or reject owners
@user_passes_test(lambda user: user.is_superuser)
def approve_owner(request, owner_id):
    try:
        owner = Onwer.objects.get(id=owner_id)
        if request.method == "POST":
            action = request.POST.get('action')
            if action == 'approve':
                owner.status = 'approved'
                owner.save()
            elif action == 'reject':
                owner.status = 'rejected'
                owner.save()
        return redirect('manage_owners')  # Redirect back to manage owners page
    except Onwer.DoesNotExist:
        return redirect('manage_owners')  # If owner not found, redirect to manage owners
    
def user_login(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        # Check in User model
        user = User.objects.filter(email=email).first()

        if user and check_password(password, user.password):
            # Log the user in directly, since password is valid
            login(request, user)  # Log the user in
            messages.success(request, "Login successful!")
            return redirect('dashboard_user')  # Redirect to the dashboard

        # If user is not authenticated
        messages.error(request, "Invalid credentials")
        return redirect('user_login')
    
    next_url = request.GET.get('next', '')
    return render(request, 'myApp/login_user.html', {'next': next_url})

def user_logout(request):
    # Log out the user
    auth_logout(request)
    # Redirect to the homepage or login page
    return redirect('index')


def owner_login(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        # Find owner by email
        owner = Onwer.objects.filter(email=email).first()

        if owner:
            # Check if the account is approved
            if owner.status == 'approved':
                # Check the password
                if check_password(password, owner.password):
                    # Log in by creating a session manually
                    request.session['owner_id'] = owner.id
                    messages.success(request, "Login successful!")
                    return redirect('dashboard_owner')
                else:
                    messages.error(request, "Invalid credentials: Incorrect password.")
            elif owner.status == 'pending':
                messages.warning(request, "Your account is still pending approval.")
            else:
                messages.error(request, "Your account has been rejected. Please contact admin.")
        else:
            messages.error(request, "Invalid credentials: Owner not found.")

    return render(request, 'myApp/login_owner.html')

@login_required
def delete_room(request, room_id):
    room = get_object_or_404(Room, id=room_id, hotel__owner=request.user)
    room.delete()
    messages.success(request, "Room deleted successfully.")
    return redirect('dashboard_owner')

@login_required
def edit_room(request, room_id):
    room = get_object_or_404(Room, id=room_id, hotel__owner=request.user)

    if request.method == 'POST':
        room.room_type = request.POST.get('room_type')
        room.room_count = request.POST.get('room_count')
        room.facilities = request.POST.get('facilities')
        if 'photos' in request.FILES:
            room.photos = request.FILES['photos']
        room.save()
        messages.success(request, "Room updated successfully.")
        return redirect('dashboard_owner')

    context = {'room': room}
    return render(request, 'myApp/edit_room.html', context)