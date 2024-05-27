from django import forms

from .models import Rating, Amenity, LocationType
from core.models import User

from django.core.exceptions import ValidationError
from datetime import date

BOOK_ROOM_INPUT_CLASSES = 'w-full mb-2 py-1 px-3 rounded-xl bg-gray-400 text-gray-800 border'
INPUT_CLASSES = 'w-full px-3 rounded-lg bg-gray-400 text-gray-800 border'


class BookRoomForm(forms.Form):
    start_date = forms.DateField(widget=forms.DateInput(attrs={
        'type': 'date',
        'placeholder': 'Enter your check-in date...',
        'class': BOOK_ROOM_INPUT_CLASSES
    }))

    end_date = forms.DateField(widget=forms.DateInput(attrs={
        'type': 'date',
        'placeholder': 'Enter your check-out date...',
        'class': BOOK_ROOM_INPUT_CLASSES
    }))

    def clean(self):
        cleaned_data = super().clean()
        check_in = cleaned_data.get('start_date')
        check_out = cleaned_data.get('end_date')

        if check_in and check_out:
            if check_in < date.today():
                raise ValidationError('The check-in date cannot be in the past.')
            
            if check_out <= check_in:
                raise ValidationError("Check-out date must be after check-in date.")
            
        return cleaned_data
    

class RatingForm(forms.ModelForm):
    class Meta:
        model = Rating
        fields = ('cleanliness', 'service', 'location', 'amenities', 'room_quality', 'comment')
        widgets = {
            'cleanliness': forms.NumberInput(attrs={
                'class': INPUT_CLASSES,
                'placeholder': 'Rate between 1-5',
            }),

            'service': forms.NumberInput(attrs={
                'class': INPUT_CLASSES,
                'placeholder': 'Rate between 1-5',
            }),

            'location': forms.NumberInput(attrs={
                'class': INPUT_CLASSES,
                'placeholder': 'Rate between 1-5',
            }),

            'amenities': forms.NumberInput(attrs={
                'class': INPUT_CLASSES,
                'placeholder': 'Rate between 1-5',
            }),

            'room_quality': forms.NumberInput(attrs={
                'class': INPUT_CLASSES,
                'placeholder': 'Rate between 1-5',
            }),

            'comment': forms.Textarea(attrs={
                'class': 'w-full h-[150px] px-3 py-2 rounded-lg bg-gray-400 text-gray-800 border',
                'placeholder': 'Add a comment. Thank you...',
            }),
        }

    def clean(self):
        clean_data = super().clean()
        for field_name in ['cleanliness', 'service', 'location', 'amenities', 'room_quality']:
            rating = clean_data.get(field_name)
            if rating is not None and (rating < 1 or rating > 5):
                self.add_error(field_name, forms.ValidationError(f"{field_name.capitalize()} rating must be between 0 and 5."))


class HotelFilterForm(forms.Form):
    amenities = forms.ModelMultipleChoiceField(
        queryset=Amenity.objects.all(),
        widget = forms.CheckboxSelectMultiple(attrs={'onchange': 'this.form.submit();'}),
        required = False
    )

    location_types = forms.MultipleChoiceField(
        choices=LocationType.choices,
        widget=forms.CheckboxSelectMultiple(attrs={'onchange': 'this.form.submit();'}),
        required=False,
        label="Location Types"
    )













class AddUserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('email', 'name', 'role', 'password',)
        widgets = {
            'email': forms.EmailInput(attrs={
                'placeholder': 'Email address...',
                'class': INPUT_CLASSES
            }),

            'name': forms.TextInput(attrs={
                'placeholder': 'Name...',
                'class': INPUT_CLASSES
            }),

            'role': forms.Select(attrs={
                'class': INPUT_CLASSES
            }),

            'password': forms.PasswordInput(attrs={
                'placeholder': 'Enter a password...',
                'class': INPUT_CLASSES
            }),
        }


class EditUserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('email', 'name', 'role',)
        widgets = {
            'email': forms.EmailInput(attrs={
                'placeholder': 'Email address...',
                'class': INPUT_CLASSES
            }),

            'name': forms.TextInput(attrs={
                'placeholder': 'Name...',
                'class': INPUT_CLASSES
            }),

            'role': forms.Select(attrs={
                'class': INPUT_CLASSES
            }),
        }