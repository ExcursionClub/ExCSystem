from collections import OrderedDict
import json

from core.convinience import get_all_rfids
from core.forms.fields.RFIDField import RFIDField
from core.models import Member, Staffer
from core.models.QuizModels import Question
from django import forms
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from django.urls import reverse
from django.utils.timezone import timedelta
from ExCSystem.settings import WEB_BASE
from phonenumber_field.formfields import PhoneNumberField
from phonenumber_field.widgets import PhoneNumberPrefixWidget


class MemberCreationForm(forms.ModelForm):
    """
    A form for creating new members. Includes all the required
    fields, plus a repeated password.

    This uses the ModelForm (like the rest of django's admin) to automatically translate the model into a Form, View and
    the related HTML. Therefore, what is contained here simply overrides some default functionality, and explicit views
    and templates may not be present.
    """

    # TODO: Make these either editable in the admin or be sourced externally
    membership_choices = (
        ("year_new",        "$60 - Full Year New"),
        ("year_return",     "$40 - Full Year Returning"),
        ("quarter_new",     "$30 - One Quarter New"),
        ("quarter_return",  "$20 - One Quarter Returning")
    )

    username = forms.EmailField(label='Email')
    rfid = RFIDField(
        label='RFID',
        help_text='If you\'re renewing, this will replace your current rfid tag',
        required=False
    )
    password1 = forms.CharField(
        label='Password',
        widget=forms.PasswordInput,
        help_text="You can skip this if you're renewing",
        required=False
    )
    password2 = forms.CharField(
        label='Confirm Password',
        widget=forms.PasswordInput,
        help_text="You can skip this if you're renewing",
        required=False
    )
    membership = forms.ChoiceField(label="Membership Payment", choices=membership_choices)

    membership_duration = 0
    referenced_member = None

    class Meta:
        model = Member
        fields = ('username', 'password1', 'password2', 'membership', 'rfid')

    def clean_username(self):
        email = self.cleaned_data['username']

        # If a member exists with this email, we will be extendign their membership, so save them for future reference
        current = Member.objects.filter(email=email)
        if current:
            self.referenced_member = current[0]

        return email

    def clean_rfid(self):
        rfid = self.cleaned_data['rfid']

        if rfid in get_all_rfids():
            raise forms.ValidationError("This RFID is already in use!")

        # If a member is renewing, the RFID can either be a new rfid, or empty
        if self.referenced_member and not (len(rfid) == 0 or len(rfid) == 10):
            raise forms.ValidationError

        # If a member is not renewing, then rfid must be present
        if not self.referenced_member and len(rfid) != 10:
            raise forms.ValidationError("This is not a valid 10 digit RFID!")

        return rfid

    def clean_password1(self):
        """Passwords are required if the member is new"""
        password = self.cleaned_data['password1']
        if not self.referenced_member and not password:
            raise forms.ValidationError("Password is required when you're signing up")
        return password

    def clean_password2(self):
        # Check that the two password entries match
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords don't match")
        return password2

    def clean_membership(self):
        """
        Convert the membership selection into a timedelta, and verify it is valid for the members current status
        """
        selection = self.cleaned_data['membership']

        # Convert the membership selection into a timedelta
        if "year" in selection:
            self.membership_duration = timedelta(days=365)
        elif "quarter" in selection:
            self.membership_duration = timedelta(days=90)
        else:
            raise forms.ValidationError("Invalid membership choice!")

        if self.is_new_membership(selection) and self.referenced_member:
            raise forms.ValidationError(
                "A member with this email already exists! Make sure you selected the right membership!")
        elif not self.is_new_membership(selection) and not self.referenced_member:
            raise forms.ValidationError(
                "Could not find the member! Please make sure you typed the email correctly!"
            )

    @staticmethod
    def is_new_membership(membership):
        """Returns true if the membership selection corresponds to a new member signing up"""
        return "new" in membership

    def save(self, commit=True):
        """
        Save the newly created member
        :param commit: This is ignored, we always commit
        """

        # We will always commit the save, so make sure m2m fields are always saved
        self.save_m2m = self._save_m2m

        email = self.cleaned_data['username']
        rfid = self.cleaned_data['rfid']
        password = self.cleaned_data['password1']
        duration = self.membership_duration

        # Depending on if this member exists or not, either create a new member, or just extend the membership
        if self.referenced_member:
            member = self.referenced_member
            member.extend_membership(duration, rfid=rfid, password=password)
        else:
            member = Member.objects.create_member(email, rfid, duration, password)

        finish_url = WEB_BASE + reverse("admin:core_member_finish", kwargs={'pk': member.pk})
        member.send_intro_email(finish_url)
        member.save()
        return member


class MemberFinishForm(forms.ModelForm):
    """
    Form used to let the member finish their account setup

    To finish setting up their account, members must submit all missing data (ie phone number) and successfully complete
    a quiz about the rules of the club.

    This uses the ModelForm (like the rest of django's admin) to automatically translate the model into a Form, View and
    the related HTML. Therefore, what is contained here simply overrides some default functionality, and explicit views
    and templates may not be present.
    """

    member_field_names = ['first_name', 'last_name', 'phone_number', 'image']

    # Instantiate the non-default member data fields
    phone_number = PhoneNumberField(widget=PhoneNumberPrefixWidget)

    # Instantiate the quiz fields
    questions = Question.objects.filter(usage="membership")

    # Limit the size of the uploaded image, currently set to 20MB
    # TODO: Move to utils
    max_image_MB = 20
    max_image_bytes = max_image_MB * 1048576

    def __init__(self, *args, **kwargs):
        super(MemberFinishForm, self).__init__(*args, **kwargs)

        self.quiz_field_names = []
        for question in self.questions:

            # Dynamically insert a choice field for each of the questions
            self.fields[question.name] = forms.ChoiceField(label=question.question_text, choices=question.get_choices())
            self.quiz_field_names.append(question.name)

            # Dynamically insert a function for django to call to validate the answer for each of these fields
            setattr(self, "clean_{}".format(question.name), self.get_question_cleaner(question.name))

    # This meta class allows the django backend to link this for to the model
    class Meta:
        model = Member
        fields = ('first_name', 'last_name', 'phone_number', 'image')

    def as_table_member(self):
        """Make it possible to get the HTML of just the member information section of this form"""
        return self.as_table_subset(self.member_field_names)

    def as_table_quiz(self):
        """Make it possible to get the HTML of just the quiz information section of this form"""
        return self.as_table_subset(self.quiz_field_names)

    def as_table_subset(self, subset_field_names):
        """Run the forms html generator, temporarily substituting a subset of the fields for all fields"""
        original_fields = self.fields
        html = ''

        try:
            self.fields = self.get_fields_subset(subset_field_names)
            html = self._html_output(
                normal_row='<tr%(html_class_attr)s><th>%(label)s</th><td>%(errors)s%(field)s%(help_text)s</td></tr>',
                error_row='<tr><td colspan="2"><font color="red">%s</font></td></tr>',
                row_ender='</td></tr>',
                help_text_html='<br /><span class="helptext">%s</span>',
                errors_on_separate_row=False
            )
        finally:
            self.fields = original_fields

        return html

    def get_fields_subset(self, field_name_list):
        fields_subset = OrderedDict()
        for name in field_name_list:
            fields_subset[name] = self.fields[name]
        return fields_subset

    def get_question_cleaner(self, question_name):
        """Generic function that validates whether a quiz question was answered correctly"""

        def cleaner():
            given_answer = self.cleaned_data[question_name]
            question = Question.objects.get(name=question_name)

            if not question.is_correct(given_answer):
                raise forms.ValidationError(question.error_message)

        return cleaner

    def clean_image(self):
        # TODO: Move to utils
        """Ensures that the image is of a sufficiently small size before it gets uploaded"""
        image = self.cleaned_data['image']

        if image.size > self.max_image_bytes:
            raise forms.ValidationError(f"Selected image is too large! Max {self.max_image_MB}MB")

        return image

    def save(self, commit=True):
        # We will always commit the save, so make sure m2m fields are always saved
        self.save_m2m = self._save_m2m

        member = self.instance
        member.first_name = self.cleaned_data['first_name']
        member.last_name = self.cleaned_data['last_name']
        member.phone_number = self.cleaned_data['phone_number']
        member.image = self.cleaned_data['image']
        member = member.promote_to_active()

        member.save()
        return member


class MemberChangeRFIDForm(forms.ModelForm):
    """
    Form to expedite the process of changing a users RFID tag

    This form allows a member to replace a lost or missing RFID tag. Note: a member cannot have more than one RFID

    This uses the ModelForm (like the rest of django's admin) to automatically translate the model into a Form, View and
    the related HTML. Therefore, what is contained here simply overrides some default functionality, and explicit views
    and templates may not be present.
    """

    class Meta:
        model = Member
        fields = ('rfid', )


class MemberChangeCertsForm(forms.ModelForm):
    """
    Form to add/remove certifications from the member

    This uses the ModelForm (like the rest of django's admin) to automatically translate the model into a Form, View and
    the related HTML. Therefore, what is contained here simply overrides some default functionality, and explicit views
    and templates may not be present.
    """

    class Meta:
        model = Member
        fields = ('certifications', )


class MemberUpdateContactForm(forms.ModelForm):
    """
    Form to expedite the process of updating a members contact info (email, phone)

    This uses the ModelForm (like the rest of django's admin) to automatically translate the model into a Form, View and
    the related HTML. Therefore, what is contained here simply overrides some default functionality, and explicit views
    and templates may not be present.
    """

    class Meta:
        model = Member
        fields = ('email', 'phone_number')


class MemberChangeGroupsForm(forms.ModelForm):
    """
    Form to change the status of a member, and dispatch any additional data requirements

    This form should only be accessible to users with high status (board or above) and allows them to change the status
    of the member in the system. Once the form is submitted further data processing is dispatched based on the change in
    status.
    Ex:
        If a Member becomes a staffer, then they are emailed a form with additional staffer information.
        If a Staffer is demoted, then their associated staff profile is removed.

    """

    class Meta:
        model = Member
        fields = ('groups',)


class StafferDataForm(forms.ModelForm):
    """
    Form to request the additional information required when becoming a staffer.

    A link to this form should be emailed to a member when they are upgraded to a staffer, or when a staffer wishes to
    edit their description or other staff data.

    This uses the ModelForm (like the rest of django's admin) to automatically translate the model into a Form, View and
    the related HTML. Therefore, what is contained here simply overrides some default functionality, and explicit views
    and templates may not be present.
    """

    exc_email = forms.CharField(
        label="Staffer Nickname",
        max_length=20,
        help_text="The name of the staffer: to be used as the beginning of the email address"
    )

    class Meta:
        model = Staffer
        # Member should already be known when this form is accessed, so having it as a field is excessive
        fields = ('exc_email', 'autobiography')

    def clean_exc_email(self):
        """
        Although the field is named exc_email, the input should only be the staff name, so append rest of email here
        """
        staff_name = self.cleaned_data['exc_email']
        return staff_name + "@excursionclubucsb.org"


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
                  'first_name',
                  'last_name',
                  'phone_number',
                  'rfid',
                  'groups',
                  'image')

    def clean_groups(self):
        groups = self.cleaned_data['groups']
        if len(groups) != 1:
            raise forms.ValidationError('Each member must be in exactly one group!')
        self.cleaned_data['group'] = str(groups[0])
        return groups

    def save(self, commit=True):
        self.instance.move_to_group(self.cleaned_data['group'])
        return super(MemberChangeForm, self).save(commit=commit)
