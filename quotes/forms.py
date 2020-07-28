from django.forms import ModelForm
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django import forms
from .models import Stock,NewStock

class CreateUserForm (UserCreationForm):
	class Meta:
		model = User
		fields = ['username', 'email', 'password1', 'password2']

class StockForm(forms.ModelForm):
	class Meta:
		model = Stock
		fields = ['ticker']

class NewStockForm(forms.ModelForm):
	class Meta:
		model = NewStock
		fields = ['ticker']
