from django.db import models
from django.contrib.auth.models import AbstractBaseUser,BaseUserManager
import datetime
# Create your models here.


class Users(AbstractBaseUser):
    user_id = models.BigAutoField(primary_key=True)
    username= models.CharField(max_length=30,unique=True, blank=True, null=True)
    balance = models.FloatField(default=0.0)
    is_active = models.BooleanField(default=True)
    is_superuser = models.BooleanField(default=False)

    USERNAME_FIELD = 'username'

    class Meta:
        db_table = "table_users"

    def __str__(self):
        return str(self.username)


    def has_perm(self, perm, obj=None): return self.is_superuser

    def has_module_perms(self, app_label): return self.is_superuser



class Transactions(models.Model):
    transaction_id = models.CharField(unique=True,max_length=30)
    transaction_type = models.CharField(max_length=6,choices=[("borrow","borrow"),("lend","lend")])
    transaction_date = models.DateField(default=datetime.date.today)
    transaction_status = models.CharField(max_length=6,choices=[("paid","paid"),("unpaid","unpaid")])
    transaction_from = models.ForeignKey(Users,on_delete=models.CASCADE,related_name="users_from")
    transaction_with = models.ForeignKey(Users,on_delete=models.CASCADE,related_name="users_with")
    transaction_amount = models.FloatField(default=0)
    reason = models.CharField(max_length=100)
