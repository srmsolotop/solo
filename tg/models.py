from django.db import models


class TelegramUser(models.Model):
    user_id = models.IntegerField(unique=True)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255, blank=True, null=True)
    username = models.CharField(max_length=255, blank=True, null=True)
    date_joined = models.DateTimeField(auto_now_add=True)
    is_super_admin = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)
    is_shop = models.BooleanField(default=False)

    def __str__(self):
        return self.username if self.username else "None"


class Trigger(models.Model):
    title = models.CharField(max_length=255)
    text = models.TextField()

    def __str__(self):
        return self.title


class Chat(models.Model):
    chat_id = models.CharField(max_length=2555)
    link = models.CharField(max_length=2555, null=True, blank=True)
    channel_link = models.CharField(max_length=2555, null=True, blank=True)
    photo = models.CharField(max_length=2555, null=True, blank=True)


class Shop(models.Model):
    main_chat = models.ForeignKey(Chat, on_delete=models.SET_NULL, null=True, blank=True)
    title = models.CharField(max_length=255)
    owner = models.ForeignKey(TelegramUser, on_delete=models.SET_NULL, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    operator = models.CharField(max_length=255, null=True, blank=True)
    support = models.CharField(max_length=255, null=True, blank=True)
    bot = models.CharField(max_length=255, null=True, blank=True)
    channel = models.CharField(max_length=255, null=True, blank=True)
    photo = models.CharField(max_length=2555, null=True, blank=True)
    chat = models.CharField(max_length=255, null=True, blank=True)
    reviews = models.PositiveIntegerField(default=0)
    hash = models.BooleanField(default=False)
    shish = models.BooleanField(default=False)
    lsd = models.BooleanField(default=False)
    grib = models.BooleanField(default=False)
    food = models.BooleanField(default=False)
    paused = models.BooleanField(default=False)

    class Meta:
        ordering = ['-reviews']

    def __str__(self):
        return self.title


class ShopReview(models.Model):
    user = models.ForeignKey(TelegramUser, on_delete=models.SET_NULL, null=True, blank=True)
    shop = models.ForeignKey(Shop, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)


class Rating(models.Model):
    rating_choices = (
        (1, "1"),
        (2, "2"),
        (3, "3"),
        (4, "4"),
        (5, "5")
    )
    user = models.ForeignKey(TelegramUser, on_delete=models.SET_NULL, null=True, blank=True)
    shop = models.ForeignKey(Shop, on_delete=models.SET_NULL, null=True, blank=True)
    rate = models.IntegerField(choices=rating_choices)
    created_at = models.DateTimeField(auto_now_add=True)


class AnnounceText(models.Model):
    shop = models.ForeignKey(Shop, on_delete=models.SET_NULL, null=True, blank=True)
    button = models.BooleanField(default=False)
    message_id = models.IntegerField(null=True, blank=True)
    from_chat_id = models.IntegerField(null=True, blank=True)
    on = models.BooleanField(default=False)


class Exchange(models.Model):
    username = models.CharField(max_length=255)
    link = models.CharField(max_length=255)
    user = models.ForeignKey(TelegramUser, on_delete=models.SET_NULL, null=True, blank=True)
