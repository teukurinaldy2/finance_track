from django import forms
from django.utils import timezone
from .models import Transaction, Category, SaldoAwal

class TransactionForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = ['type', 'category', 'amount', 'date', 'note']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date',}),
            'note': forms.Textarea(attrs={'rows': 3}),
        }
        labels = {
            'type': 'Type Transaction',
            'category': 'Category',
            'amount': 'Amount (Rp)',
            'date': 'Date',
            'note': 'Description',
        }

    def __init__(self, user=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['date'].initial = timezone.localdate()  # ← otomatis isi tanggal hari ini
        # FILTER KATEGORI BERDASARKAN USER YANG LOGIN
        if user:
            self.fields['category'].queryset = Category.objects.filter(user=user)
class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'type']
        labels = {
            'name': 'Name Category',
            'type': 'Type',
        }

class SaldoAwalForm(forms.ModelForm):
    class Meta:
        model = SaldoAwal
        fields = ['month', 'amount']
        widgets = {
            'month': forms.DateInput(attrs={'type': 'date'}),
        }
        labels = {
            'month': 'month (choose date 1)',
            'amount': 'Beginning Balance (Rp)',
        }
