from django.contrib.auth import get_user_model
from django.core.validators import MaxValueValidator, MinValueValidator
from django.core.exceptions import ValidationError
from django.db import models
import string
import random

def generate_token():
    characters = string.ascii_letters + string.digits
    random_string = ''.join(random.choices(characters, k=50))
    return random_string

# Create your models here.
class VideoFomats(models.Model):
    format = models.CharField(max_length=10, unique=True, blank=False)
    active = models.BooleanField(default=True)

    def __str__(self):
        return self.format

class Accounts(models.Model):
    
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    nickname = models.CharField(max_length=50)
    active = models.BooleanField(default=True)
    min_duration = models.PositiveIntegerField(default=5, blank=False,
                                                validators=[MinValueValidator(1), MaxValueValidator(50)])
    max_file_size = models.PositiveIntegerField(default=10, blank=False, 
                                                validators=[MinValueValidator(1), MaxValueValidator(20)])
    max_duration = models.PositiveIntegerField(default=60, blank=False,
                                               validators=[MinValueValidator(1), MaxValueValidator(100)])
    allowed_formats = models.ManyToManyField(VideoFomats)

    def __str__(self):
        return self.nickname


    def clean(self):
        if self.min_duration >= self.max_duration:
            raise ValidationError('Minimum Duration should be less than Max Duration')
        

class AccountTokens(models.Model):
    account = models.ForeignKey(Accounts, on_delete=models.CASCADE)
    token_name = models.CharField(max_length=25, unique=True, blank=False, null=False, default=None)
    access_token = models.CharField(max_length=50, null=False, default=generate_token)
    status = models.BooleanField(default=True)
    createdTime = models.DateTimeField(auto_now_add=True)
    updatedTime = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('account', 'token_name')

    def __str__(self):
        return self.token_name + (" - Active" if self.status else " - Inactive")