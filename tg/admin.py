from django.contrib import admin
from .models import TelegramUser, Trigger, Shop, ShopReview, Rating, Chat, AnnounceText, Exchange


@admin.register(TelegramUser)
class TelegramUserAdmin(admin.ModelAdmin):
    list_display = ['username']


@admin.register(Trigger)
class TriggerAdmin(admin.ModelAdmin):
    list_display = ['title']


@admin.register(Shop)
class ShopAdmin(admin.ModelAdmin):
    list_display = ['id', 'title']


@admin.register(ShopReview)
class ShopReviewAdmin(admin.ModelAdmin):
    list_display = ['id', 'shop', 'user', 'created_at']


@admin.register(Rating)
class RatingAdmin(admin.ModelAdmin):
    list_display = ['id']


@admin.register(Chat)
class ChatAdmin(admin.ModelAdmin):
    list_display = ['id']


@admin.register(AnnounceText)
class AnnounceAdmin(admin.ModelAdmin):
    list_display = ['id']


@admin.register(Exchange)
class ExchangeAdmin(admin.ModelAdmin):
    list_display = ['id']