from django.db import models

class userModel(models.Model):
    field1 = models.CharField(max_length=100)
    field2 = models.IntegerField()