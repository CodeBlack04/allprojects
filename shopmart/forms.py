from django import forms
from .models import Product, ConversationMessage, Contact, Category

INPUT_CLASSES = 'w-full py-4 px-6 rounded-xl bg-cyan-900'

# core forms

class ContactForm(forms.ModelForm):
    class Meta:
        model = Contact
        fields = ('full_name', 'email', 'subject', 'message')
        widgets = {
            'full_name': forms.TextInput(attrs={
                'placeholder': 'Full Name*',
                'class': INPUT_CLASSES
            }),

            'email': forms.TextInput(attrs={
                'placeholder': 'Email Address*',
                'class': INPUT_CLASSES
            }),

            'subject': forms.TextInput(attrs={
                'placeholder': 'Subject*',
                'class': INPUT_CLASSES
            }),

            'message': forms.Textarea(attrs={
                'placeholder': 'Send a message...',
                'class': INPUT_CLASSES
            }),
        }










# product forms



class NewProductForm(forms.ModelForm):
    
    class Meta:
        model = Product
        fields = ('category', 'name', 'description', 'price', 'image',)
        widgets = {
            'category': forms.Select(attrs={
                'class': INPUT_CLASSES
            }),
            'name': forms.TextInput(attrs={
                'class': INPUT_CLASSES
            }),
            'description': forms.Textarea(attrs={
                'class': INPUT_CLASSES
            }),
            'price': forms.TextInput(attrs={
                'class': INPUT_CLASSES
            }),
            'image': forms.FileInput(attrs={
                'class': INPUT_CLASSES
            })
        }

class EditProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ('name', 'description', 'price', 'image')
        widgets = {
            'name': forms.TextInput(attrs={
                'class': INPUT_CLASSES
            }),
            'description': forms.Textarea(attrs={
                'class': INPUT_CLASSES
            }),
            'price': forms.TextInput(attrs={
                'class': INPUT_CLASSES
            }),
            'image': forms.FileInput(attrs={
                'class': INPUT_CLASSES
            })
        }








# chat forms





class NewMessageForm(forms.ModelForm):
    class Meta:
        model = ConversationMessage
        fields = ('body',)
        widgets = {
            'body': forms.Textarea(attrs={
                'placeholder': 'Send a message...',
                'class': 'w-full py-4 px-6 rounded-xl border bg-cyan-950'
            })
        }




#browse forms




class CategoryForm(forms.Form):
    categories = forms.ModelMultipleChoiceField(
        queryset = Category.objects.all(),
        widget=forms.CheckboxSelectMultiple(attrs={'onChange': 'this.form.submit()'}),
        required= False,
    )