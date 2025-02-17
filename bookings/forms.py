from django import forms
from .models import Booking


class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ['check_in_date', 'check_out_date', 'guests']
        labels = {
            'check_in_date': 'Заезд',
            'check_out_date': 'Выезд',
            'guests': 'Гости',
        }
