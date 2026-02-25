from django.contrib import admin
from .models import User, Location, Expenses, AmountReceived

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'name', 'profile', 'inserted_on')
    search_fields = ('username', 'name')
    list_filter = ('profile',)
    readonly_fields = ('inserted_on',)

@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ('itinerary_name', 'user', 'inserted_on', 'updated_on')
    search_fields = ('itinerary_name', 'user__username')
    list_filter = ('user',)
    readonly_fields = ('inserted_on', 'updated_on')

@admin.register(Expenses)
class ExpensesAdmin(admin.ModelAdmin):
    list_display = ('spent_on', 'amount_spent', 'inserted_on')
    search_fields = ('spent_on',)
    readonly_fields = ('inserted_on',)
    list_filter = ('inserted_on',)

@admin.register(AmountReceived)
class AmountReceivedAdmin(admin.ModelAdmin):
    list_display = ('user', 'amount_sent', 'inserted_on')
    search_fields = ('user__username',)
    list_filter = ('user', 'inserted_on')
    readonly_fields = ('inserted_on',)
