from unittest.case import expectedFailure
from django.test import TestCase
from eventex.subscriptions.forms import SubscriptionForm
from django.core import mail

# Create your tests here.
class SubscribeTest(TestCase):
    
    def setUp(self) -> None:
        self.response = self.client.get('/inscricao/')
        
    def test_get(self):
        self.assertEqual(200, self.response.status_code)
    
    def test_template(self):
        self.assertTemplateUsed(self.response, 'subscriptions/subscription_form.html')
        
    def test_html(self):
        """HTML must contain input tags"""
        self.assertContains(self.response, '<form')
        self.assertContains(self.response, '<input', 6)
        self.assertContains(self.response, 'type="text"', 3)
        self.assertContains(self.response, 'type="email"')
        self.assertContains(self.response, 'type="submit"')
        
    def test_csrf(self):
        self.assertContains(self.response, 'csrfmiddlewaretoken')
        
    def test_has_form(self):
        form = self.response.context['form']
        self.assertIsInstance(form, SubscriptionForm)
        
    def test_form_has_fields(self):
        form = self.response.context['form']
        self.assertSequenceEqual(['name', 'cpf', 'email', 'phone'], list(form.fields))
        
class SubscribePostTest(TestCase):
    def setUp(self) -> None:
        self.data = dict(name='Murilo', cpf='12345678901', email='murilo@teste.com.br', phone='55-01-99999-9999')
        self.response = self.client.post('/inscricao/', self.data)
        
        self.email = mail.outbox[0]

    def test_post(self):
        self.assertEqual(302, self.response.status_code)
    
    def test_send_subscribe_email(self):
        self.assertEqual(1, len(mail.outbox))
    
    def test_subscription_email_subject(self):
        expect = 'Confirmação de inscrição'
        self.assertEqual(expect, self.email.subject)
    
    def test_subscription_email_from(self):
        expect = 'contato@eventex.com.br'
        self.assertEqual(expect, self.email.from_email)
    
    def test_subscription_email_to(self):
        expect = ['contato@eventex.com.br', 'murilo@teste.com.br']
        self.assertEqual(expect, self.email.to)
    
    def test_subscription_email_body(self):
        self.assertIn(self.data['name'], self.email.body)
        self.assertIn(self.data['cpf'], self.email.body)
        self.assertIn(self.data['email'], self.email.body)
        self.assertIn(self.data['phone'], self.email.body)


class SubscribeInvalidPost(TestCase):
    def setUp(self) -> None:
        self.response = self.client.post('/inscricao/', {})
    
    def test_post(self):
        self.assertEqual(200, self.response.status_code)
    
    def test_template(self):
        self.assertTemplateUsed(self.response, 'subscriptions/subscription_form.html')
        
    def test_has_form(self):
        form = self.response.context['form']
        self.assertIsInstance(form, SubscriptionForm)
        
    def test_form_has_errors(self):
        form = self.response.context['form']
        self.assertTrue(form.errors)
        
class SubscribeSucessMessage(TestCase):
    def setUp(self) -> None:
        self.sucess_data = dict(name='Murilo', cpf='12345678901', email='murilo@teste.com.br', phone='551199999-9999')
        self.response = self.client.post('/inscricao/', self.sucess_data, follow=True)
    
    def test_message(self):
        self.assertContains(self.response, 'Inscrição realizada com sucesso!')