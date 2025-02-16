from django.db import models
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User

class User(models.Model):
    first_name= models.CharField(max_length=255)
    last_name= models.CharField(max_length=255)
    email=models.CharField(max_length=255, unique=True)
    password= models.CharField(max_length=255)  
    is_owner = models.BooleanField(default=False) 
    created_at= models.DateTimeField(auto_now_add=True)
    updated_at= models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.password.startswith('pbkdf2_'):  
            self.password = make_password(self.password)
        super().save(*args, **kwargs)

class Onwer(models.Model):
    first_name= models.CharField(max_length=255)
    last_name= models.CharField(max_length=255)
    email=models.EmailField(unique=True)
    password= models.CharField(max_length=255)  
    certificate= models.ImageField(upload_to='certificates/', null=True, blank=True)
    created_at= models.DateTimeField(auto_now_add=True)
    updated_at= models.DateTimeField(auto_now=True)

    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    )
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')

    def save(self, *args, **kwargs):
        if not self.password.startswith('pbkdf2_'):  
            self.password = make_password(self.password)
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.first_name} {self.last_name} ({self.email})'
    
    
class Hotel(models.Model):
    name = models.CharField(max_length=255)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class Room(models.Model):
    ROOM_TYPES = [
        ('single', 'Single'),
        ('double', 'Double'),
        ('suite', 'Suite'),
    ]

    hotel = models.ForeignKey(Hotel, related_name='rooms', on_delete=models.CASCADE)
    room_type = models.CharField(max_length=10, choices=ROOM_TYPES)
    room_count = models.PositiveIntegerField()
    facilities = models.CharField(max_length=500)
    photos = models.ImageField(upload_to='room_photos/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.hotel.name} - {self.room_type}"
