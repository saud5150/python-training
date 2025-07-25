from allauth.socialaccount.adapter import DefaultSocialAccountAdapter

class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):
    def populate_user(self, request, sociallogin, data):
        user = super().populate_user(request, sociallogin, data)
        # Map Google 'name' to your User model's 'name' field
        if 'name' in data:
            user.name = data['name']
        elif 'given_name' in data and 'family_name' in data:
            user.name = f"{data['first_name']} {data['last_name']}"
        return user