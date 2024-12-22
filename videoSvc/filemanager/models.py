from django.db import models
from common.models import Accounts

# Create your models here.
class Files(models.Model):
    file_name = models.CharField(max_length=50)
    # content_type = models.CharField(max_length=50)
    file_path = models.CharField(max_length=250)

    def __str__(self):
        return self.file_name + " - " + str(self.id)
    
class AccountFiles(models.Model):
    account = models.ForeignKey(Accounts, on_delete=models.CASCADE)
    file = models.ForeignKey(Files, on_delete=models.CASCADE)
    createdTime = models.DateTimeField(auto_now_add=True)
    updatedTime = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ('account', 'file')
    
    def __str__(self):
        return  self.account.nickname  + " - " + self.file.file_name

