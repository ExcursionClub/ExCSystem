from copy import deepcopy

from uwccsystem.settings import CLUB_EMAIL
from core.models.FileModels import AlreadyUploadedImage
from django.forms import widgets
from django.urls import reverse


class RFIDWidget(widgets.TextInput):
    change_button_text = "Enter Manually"
    allow_revert = True
    revert_button_text = "Hide Manual Input"
    scan_rfid_button_text = "Click to Scan RFID"
    template_name = "widgets/rfid.html"
    max_length = 10

    def __init__(self, attrs=None):
        # TODO: Add option to modify default values of class vars here
        super().__init__(attrs)

    def get_context(self, name, value, attrs):
        context = super(RFIDWidget, self).get_context(name, value, attrs)

        widget = context["widget"]
        widget["change_button_text"] = self.change_button_text
        widget["allow_revert"] = self.allow_revert
        widget["revert_button_text"] = self.revert_button_text
        widget["scan_rfid_button_text"] = self.scan_rfid_button_text
        widget["max_length"] = self.max_length

        context["widget"] = widget
        return context


class ExistingImageWidget(widgets.ChoiceWidget):
    template_name = "widgets/ExistingImageWidget.html"

    def __init__(self, image_type, attrs=None):
        super(ExistingImageWidget, self).__init__(attrs=attrs)
        self.attrs["image_type"] = image_type
        self.image_type = image_type

    def get_available_images(self):
        """
        Get a dictionary of all existing images keyed by sub_type

        For every sub_type, the dictionary will contain a list of images of that type
        """
        # To simplify, get the images already sorted by type
        images = list(
            AlreadyUploadedImage.objects.filter(image_type=self.image_type).order_by(
                "sub_type"
            )
        )

        image_options = {}
        current_type = ""
        images_this_type = []

        for img in images:
            if img.sub_type == current_type:
                images_this_type.append(img)
            else:
                # If we've reached a new image type, save the accumulated images to image_options and update the type
                image_options[current_type] = deepcopy(images_this_type)
                images_this_type = [img]
                current_type = img.sub_type

        # Also save the last set of images
        image_options[current_type] = deepcopy(images_this_type)

        # Remove the empty list that gets created with the initial "" gear type
        del image_options[""]

        return image_options

    def get_context(self, name, value, attrs):
        context = super(ExistingImageWidget, self).get_context(name, value, attrs)
        context["image_options"] = self.get_available_images()
        context["add_image_url"] = reverse("admin:core_alreadyuploadedimage_add")
        return context


class GearImageWidget(ExistingImageWidget):
    def __init__(self, attrs=None):
        super(GearImageWidget, self).__init__("gear", attrs=attrs)


class ExCEmailWidget(widgets.TextInput):
    template_name = "widgets/exc_email.html"

    def __init__(self, *args, **kwargs):
        self.email_tail = CLUB_EMAIL
        super(ExCEmailWidget, self).__init__(*args, **kwargs)

    def get_context(self, name, value, attrs):
        context = super(ExCEmailWidget, self).get_context(name, value, attrs)
        context['email_tail'] = self.email_tail
        return context


