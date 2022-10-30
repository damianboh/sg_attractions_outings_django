from socket import fromshare
from django import forms

class SearchForm(forms.Form):
    term = forms.CharField(required=False)