from allauth.account.adapter import DefaultAccountAdapter
from django.contrib.auth.models import Group
from store.models import DeliveryMan

class CustomAccountAdapter(DefaultAccountAdapter):
    def save_user(self, request, user, form, commit=True):
        user = super().save_user(request, user, form, commit)
        # Assign users to 'DeliveryGroup' if they are intended to be delivery men
        # This logic can be expanded, e.g., based on a specific signup form field
        # For now, let's assume we'll manually add users to this group, or
        # there's another mechanism to designate them as delivery men.
        # This adapter mainly ensures that if a user is part of 'DeliveryGroup',
        # a DeliveryMan profile is created for them.
        
        # Check if the user is part of the 'DeliveryGroup' and create DeliveryMan profile if not exists
        delivery_group, created = Group.objects.get_or_create(name='DeliveryGroup')
        if delivery_group in user.groups.all():
            DeliveryMan.objects.get_or_create(user=user)
            
        return user
