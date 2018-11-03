from django.db import models


class AlreadyUploadedImage(models.Model):

    image = models.ImageField()
    upload_date = models.DateTimeField(auto_now_add=True)

    image_type = models.CharField(
        max_length=10,
        choices=(
            ("gear", "Gear Image"),
            ("other", "Other Image")
        )
    )
    sub_type = models.CharField(max_length=20, default="Unknown")

    @property
    def name(self):
        return self.image.name

    @property
    def url(self):
        return self.image.url



