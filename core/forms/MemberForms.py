from django import forms
from core.models import Member
from django.contrib.auth.forms import ReadOnlyPasswordHashField


class MemberCreationForm(forms.ModelForm):
    """
    A form for creating new members. Includes all the required
    fields, plus a repeated password.

    This uses the ModelForm (like the rest of django's admin) to automatically translate the model into a Form, View and
    the related HTML. Therefore, what is contained here simply overrides some default functionality, and explicit views
    and templates may not be present.
    """

    username = forms.EmailField(label='Email', widget=forms.EmailInput)
    rfid = forms.CharField(label='RFID', max_length=10)
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Confirm Password', widget=forms.PasswordInput)

    class Meta:
        model = Member
        fields = ('username', 'rfid', 'password1', 'password2',)

    def clean_email(self):
        email = self.cleaned_data['username']
        return email

    def clean_password2(self):
        # Check that the two password entries match
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords don't match")
        return password2

    def save(self, commit=True):
        # Save the provided password in hashed format
        print(self.errors)
        user = super(MemberCreationForm, self).save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


class MemberFinishForm(forms.Form):
    """
    Form used to let the member finish their account setup

    To finish setting up their account, members must submit all missing data (ie phone number) and successfully complete
    a quiz about the rules of the club.
    """

    pass


class MemberChangeRFIDForm(forms.Form):
    """
    Form to expedite the process of changing a users RFID tag

    This form allows a member to replace a lost or missing RFID tag. Note: a member cannot have more than one RFID
    """

    pass


class MemberUpdateContactForm(forms.Form):
    """
    Form to expedite the process of updating a members contact info (email, phone)
    """

    pass


class MemberChangeStatusForm(forms.Form):
    """
    Form to change the status of a member, and dispatch any additional data requirements

    This form should only be accessible to users with high status (board or above) and allows them to change the status
    of the member in the system. Once the form is submitted further data processing is dispatched based on the change in
    status.
    Ex:
        If a Member becomes a staffer, then they are emailed a form with additional staffer information.
        If a Staffer is demoted, then their associated staff profile is removed.

    """

    pass


class StafferDataForm(forms.ModelForm):
    """
    Form to request the additional information required when becoming a staffer.

    A link to this form should be emailed to a member when they are upgraded to a staffer, or when a staffer wishes to
    edit their description or other staff data.

    This uses the ModelForm (like the rest of django's admin) to automatically translate the model into a Form, View and
    the related HTML. Therefore, what is contained here simply overrides some default functionality, and explicit views
    and templates may not be present.
    """

    class Meta:
        model = Staffer

    pass


class MemberChangeForm(forms.ModelForm):
    """
    A form for changing members. Includes all fields, except password is hashed.

    This form can change pretty much anything about the member and exposes all the data. Therefore it should only be
    used in unexpected/unusual circumstances, and all expected/common changes should have their dedicated form.

    This uses the ModelForm (like the rest of django's admin) to automatically translate the model into a Form, View and
    the related HTML. Therefore, what is contained here simply overrides some default functionality, and explicit views
    and templates may not be present.
    """
    password = ReadOnlyPasswordHashField()

    class Meta:
        model = Member
        fields = ('email',
                  'password',
                  'first_name',
                  'last_name',
                  'phone_number',
                  'rfid',
                  'status',
                  'picture')

    def clean_password(self):
        # Regardless of what the user provides, return the initial value.
        # This is done here, rather than on the field, because the
        # field does not have access to the initial value
        return self.initial["password"]

