from os import path

from django.db import models


def get_upload_path(instance, filename):
    img_type = instance.image_type.capitalize()
    file_format = filename.split(".")[-1]
    name = instance.name.\
        replace(' ', '_').\
        replace('\\', '')
    file_path = path.join(f"{img_type}Pics", f"{name}.{file_format}")
    return file_path


class AlreadyUploadedImage(models.Model):

    name = models.CharField(max_length=50, unique=True)
    image = models.ImageField(
        upload_to=get_upload_path
    )
    upload_date = models.DateTimeField(auto_now_add=True)

    image_type = models.CharField(
        max_length=10,
        choices=(
            ("gear", "Gear Image"),
            ("other", "Other Image")
        )
    )
    sub_type = models.CharField(
        max_length=20,
        default="Unknown",
        help_text="Specific image category: i.e. Skis, Tent, Sleeping Bag etc."
    )

    @property
    def url(self):
        return self.image.url