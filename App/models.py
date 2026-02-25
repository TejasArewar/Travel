from django.db import models
from django.contrib.auth.hashers import make_password

class User(models.Model):
    PROFILE_CHOICES = [
        ('Admin', 'Admin'),
        ('Common Man', 'Common Man'),
    ]
    
    name = models.CharField(max_length=100)
    username = models.CharField(max_length=50, unique=True)
    password = models.CharField(max_length=255)
    profile = models.CharField(max_length=20, choices=PROFILE_CHOICES, default='Common Man')
    inserted_on = models.DateTimeField(auto_now_add=True)
    
    def save(self, *args, **kwargs):
        if not self.pk:
            self.password = make_password(self.password)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.username



class Location(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='itineraries')
    itinerary_name = models.CharField(max_length=200)
    place_data = models.JSONField(default=list)  # Stores list of places [{name, latitude, longitude, address}, ...]
    inserted_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.itinerary_name}"
    
    
    


class Expenses(models.Model):
    spent_on = models.CharField(max_length=200)
    amount_spent = models.DecimalField(max_digits=10, decimal_places=2)
    inserted_on = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.spent_on} - {self.amount_spent}"




class AmountReceived(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='amounts_received')
    amount_sent = models.DecimalField(max_digits=10, decimal_places=2)
    inserted_on = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.amount_sent}"
 
    