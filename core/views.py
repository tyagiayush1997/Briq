from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from core.serializers import RegistrationSerializer,TransactionSerailizer
from rest_framework.authtoken.models import Token
from django.db import IntegrityError
import traceback
from django.db.models import Sum
from django.db.models import Q
from core.models import Users,Transactions
import json
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from core.helpers.util import creditscore
# Create your views here.
import logging
logger = logging.getLogger(__name__)

class RegisterView(APIView):
    '''
        This View is to register a user in application.
        body:
            username : Username you want to assign to your user
            password : password for your user
    '''
    def post(self,request):
        try:
            data = {}
            serializer = RegistrationSerializer(data=request.data)
            if serializer.is_valid():
                account = serializer.save()
                account.is_active = True
                account.set_password(request.data["password"])
                account.save()
                token = Token.objects.get_or_create(user=account)[0].key
                data["message"] = "user registered successfully"
                data["username"] = account.username
                data["token"] = token

            else:
                data = serializer.errors


            return Response(data)
        except KeyError as e:
            logger.error(traceback.format_exc())
            return  Response({"messsage": "Field {} missing".format(str(e))},500)
        except Exception as e:
            logger.error(traceback.format_exc())
            return Response({"message":"Issue occured while creating user {}".format(str(e))},500)

class LoginView(APIView):
    '''
        This View is to login a user into application.
        body:
            username : Username for the user you want to login
            password : password for your user
    '''
    def post(self,request):
        try:
            data = {}
            body = json.loads(request.body)
            username = body['username']
            password = body['password']
            try:

                Account = Users.objects.get(username=username)
            except BaseException as e:
                raise Exception({"400": str(e)})

            token = Token.objects.get_or_create(user=Account)[0].key
            if not Account.check_password(password):
                return Response({"message": "Incorrect Login credentials"},401)

            if Account:
                if Account.is_active:
                    data["message"] = "Success"
                    data["username"] = Account.username
                    data["user_id"] = Account.user_id
                    Res = {"data": data, "token": token}

                    return Response(Res)

                else:
                    raise Exception({"400": 'Account not active'})

            else:
                return Response({"message": 'Account doesnt exist'},400)
        except Exception as e:
            logger.error(traceback.format_exc())
            return Response({"message":"Issue occured while creating user {}".format(str(e))},500)


class TransactionList(generics.ListAPIView):
    '''
        This View is to return all transactions for the user logged in application.
        params:
            No params required
        get_queryset : Filters all the transactions belonging to logged in user.
    '''
    serializer_class = TransactionSerailizer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Transactions.objects.filter(Q(transaction_from=user.user_id) | Q(transaction_with=user.user_id))


class Transaction(APIView):
    '''
        This View is to save a transaction for this logged in user.
        Body:
            transaction_id : Unique id for transaction
            transaction_type : Type of transaction (borrow/lend)
            transaction_amount : Amount (negative, positive)
            transaction_date : AutoAdded
            transaction_status : Status of transaction (paid/unpaid)
            transaction_with : Transaction with user (user_id)
    '''
    permission_classes=[IsAuthenticated]
    def post(self,request):
        try:
            body = json.loads(request.body)
            data = request.data
            data["transaction_from"] = request.user.user_id
            serializer = TransactionSerailizer(data=data)
            resp_data= {}
            if serializer.is_valid():
                transaction = serializer.save()
                if transaction.transaction_status == "paid":
                    user1 = Users.objects.get(user_id=self.request.user.user_id)
                    user2 = Users.objects.get(user_id=transaction.transaction_with.user_id)
                    if transaction.transaction_type.lower() == "borrow":
                        user1.balance = user1.balance - transaction.transaction_amount
                        user2.balance = user2.balance + transaction.transaction_amount
                    else:
                        user2.balance = user2.balance - transaction.transaction_amount
                        user1.balance = user1.balance + transaction.transaction_amount
                    user1.save()
                    user2.save()
                resp_data["message"] = "Transactions Saved Successfully"
                resp_data["transaction_id"] = transaction.transaction_id
                return Response(data)
            else:
                data = serializer.errors
                return Response(data,400)
        except Exception as e:
            logger.error(traceback.format_exc())
            return Response({"message":"Issue occured while creating transaction {}".format(str(e))},500)

class CreditScore(APIView):
    '''
        This View is to generate credit score for the User
        params:
            Not required
    '''
    permission_classes=[IsAuthenticated]
    def get(self,request):
        try:
            user_id = request.user.user_id
            sum_lend = Transactions.objects.filter(Q(transaction_type="lend") & Q(transaction_status="paid")).aggregate(Sum('transaction_amount'))
            sum_borrow = Transactions.objects.filter(Q(transaction_type="borrow") & Q(transaction_status="paid")).aggregate(Sum('transaction_amount'))
            user_lend = Transactions.objects.filter(Q(transaction_from=user_id) & Q(transaction_type="lend") & Q(transaction_status="paid")).aggregate(Sum('transaction_amount'))
            user_borrow = Transactions.objects.filter(Q(transaction_from=user_id) & Q(transaction_type="borrow") & Q(transaction_status="paid")).aggregate(Sum('transaction_amount'))
            return Response({"creditscore":creditscore(sum_lend,sum_borrow,user_lend,user_borrow)})
        except Exception as e:
            logger.error(traceback.format_exc())
            return Response({"message":"Issue occured while updating transaction {}".format(str(e))},500)


class TransactionUpdate(APIView):
    '''
        This View is to Update a transaction status for a user in application.
        body:
            transaction_id : Transaction_id for the transaction
    '''
    permission_classes=[IsAuthenticated]
    def put(self,request):
        try:
            body = json.loads(request.body)
            transaction_id = body["transaction_id"]
            Transaction = Transactions.objects.get(transaction_id=transaction_id)
            user1 = Users.objects.get(user_id=Transaction.transaction_from.user_id)
            user2 = Users.objects.get(user_id=Transaction.transaction_with.user_id)
            if Transaction.transaction_type.lower() == "borrow":
                user1.balance = user1.balance - Transaction.transaction_amount
                user2.balance = user2.balance + Transaction.transaction_amount
            else:
                user1.balance = user1.balance + Transaction.transaction_amount
                user2.balance = user2.balance - Transaction.transaction_amount
            user1.save()
            user2.save()
            return Response({"status":"Transaction status updated successfully"})
            if Transaction:
                Transaction.transaction_status = "paid"
                Transaction.save()
                return Response({"Status":"Transaction status updated successfully"})
            else:
                raise Exception("Transaction with this id doesn't exist")
        except Exception as e:
            logger.error(traceback.format_exc())
            return Response({"message":"Issue occured while updating transaction {}".format(str(e))},500)
