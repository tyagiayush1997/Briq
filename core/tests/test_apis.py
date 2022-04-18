import unittest
from django.test import  Client
from core.models import Users,Transactions
import pytest
from django.urls import reverse
import json
import random
@pytest.mark.django_db
class BaseFunctionalAPITest(unittest.TestCase):
    def setUp(self):
        self.user = Users.objects.create(username="testing")
        self.user.set_password("testing")
        self.user.save()
        self.user2 = Users.objects.create(username="testing2")
        self.user2.set_password("testing")


        self.user2.save()
        self.client = Client()
        self.credentials = {"username": "testing","password":"testing"}
        resp = self.client.post('/login/', content_type='application/json',data = json.dumps(self.credentials))
        self.token = resp.data['token']
        self.auth_headers = {'HTTP_AUTHORIZATION': 'Token {}'.format(self.token)}
        for i in range(1):
            trans = Transactions.objects.create(transaction_id=random.randint(1,20000),transaction_type="lend",transaction_status="paid",transaction_from=self.user,transaction_with=self.user2,transaction_amount=100)
            trans.save()
        for i in range(1):
            trans = Transactions.objects.create(transaction_id=random.randint(21000,40000),transaction_type="lend",transaction_status="paid",transaction_from=self.user2,transaction_with=self.user,transaction_amount=100)
            trans.save()





    def test_a_login_api_success(self):
        response = self.client.post(reverse('login'), content_type='application/json',data = json.dumps(self.credentials))
        self.assertEqual(response.status_code, 200)

    def test_b_login_api_failure(self):
        response = self.client.post(reverse('login'), content_type='application/json',data = json.dumps({'username': "testing","password":"testing101"}))
        self.assertEqual(response.status_code, 401)


    def test_c_get_transactions_api_success(self):
        response = self.client.get(reverse('gettransaction'),**self.auth_headers)
        self.assertEqual(response.status_code, 200)

    def test_d_add_transactions_api_success(self):
        response = self.client.post(reverse('addtransaction'),content_type='application/json',data = json.dumps({"transaction_id":"12345678","transaction_type":"borrow","transaction_status":"unpaid","transaction_with":self.user2.user_id,"reason":"fun"}),**self.auth_headers)
        self.assertEqual(response.status_code, 200)

    def test_e_add_transactions_api_failure(self):
        response = self.client.post(reverse('addtransaction'),content_type='application/json',data = json.dumps({"transaction_id":"123456789","transaction_type":"b","transaction_status":"unpaid","transaction_with":self.user2.user_id,"reason":"fun"}),**self.auth_headers)
        self.assertEqual(response.status_code, 400)

    def test_f_transactions_update_api_success(self):
        response = self.client.post(reverse('addtransaction'),content_type='application/json',data = json.dumps({"transaction_id":"12345678","transaction_type":"borrow","transaction_status":"unpaid","transaction_with":self.user2.user_id,"reason":"fun"}),**self.auth_headers)
        self.assertEqual(response.status_code, 200)
        response = self.client.put(reverse('updatetransaction'),content_type='application/json',data = json.dumps({"transaction_id":"12345678"}),**self.auth_headers)
        self.assertEqual(response.status_code, 200)

    def test_g_credit_score_api_success(self):
        response = self.client.post(reverse('addtransaction'),content_type='application/json',data=json.dumps({"transaction_id":"12345678","transaction_type":"borrow","transaction_status":"paid","transaction_with":self.user2.user_id,"reason":"fun"}),**self.auth_headers)
        self.assertEqual(response.status_code, 200)
        response = self.client.get(reverse('creditscore'),**self.auth_headers)
        self.assertEqual(response.status_code, 200)
