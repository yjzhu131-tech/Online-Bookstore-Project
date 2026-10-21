from django import forms
class CheckoutForm(forms.Form):
    name = forms.CharField(max_length=150, label='Full name', widget=forms.TextInput(attrs={'autocomplete':'name','placeholder':'Your full name'}))
    email = forms.EmailField(label='Email address', widget=forms.EmailInput(attrs={'autocomplete':'email','placeholder':'you@example.com'}))
    def clean_email(self): return self.cleaned_data['email'].strip().lower()
