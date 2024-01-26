from django.db import models

class UserModel(models.Model):
    id = models.AutoField(primary_key=True)
    password = models.CharField(max_length=255)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    email = models.EmailField()

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

class BankModel(models.Model):
    id = models.AutoField(primary_key=True)
    bank_name = models.CharField(max_length=255)
    routing_number = models.CharField(max_length=20)
    swift_bic = models.CharField(max_length=20)

    def __str__(self):
        return self.bank_name

class ClientModel(models.Model):
    id_user = models.IntegerField(primary_key=True)
    id_bank = models.IntegerField()

    def __str__(self):
        return f"{self.id_user} - {self.id_bank}"