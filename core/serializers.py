
from rest_framework import serializers
from core.models import Users,Transactions

class RegistrationSerializer(serializers.ModelSerializer):

    class Meta:
        model = Users
        fields = ["username","password","user_id"]
        extra_kwargs = {"password": {"write_only": True}}


class TransactionSerailizer(serializers.ModelSerializer):

    class Meta:
        model = Transactions
        fields = ['transaction_id', 'transaction_type', 'transaction_date', 'transaction_status','reason','transaction_from','transaction_with','transaction_amount']
