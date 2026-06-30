from django import forms
from .models import ContactMessage

class ContactMessageForm(forms.ModelForm):
    class Meta:
        model = ContactMessage
        fields = ['name', 'email', 'message']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'w-full bg-transparent border-b border-[#888888]/20 focus:border-[#F5F5F5] py-3 text-[#F5F5F5] outline-none transition-colors duration-300 placeholder-[#888888]/50',
                'placeholder': 'Your Name',
                'id': 'contact-name'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'w-full bg-transparent border-b border-[#888888]/20 focus:border-[#F5F5F5] py-3 text-[#F5F5F5] outline-none transition-colors duration-300 placeholder-[#888888]/50',
                'placeholder': 'Your Email',
                'id': 'contact-email'
            }),
            'message': forms.Textarea(attrs={
                'class': 'w-full bg-transparent border-b border-[#888888]/20 focus:border-[#F5F5F5] py-3 text-[#F5F5F5] outline-none transition-colors duration-300 placeholder-[#888888]/50 h-32 resize-none',
                'placeholder': 'Your Message',
                'id': 'contact-message'
            }),
        }
