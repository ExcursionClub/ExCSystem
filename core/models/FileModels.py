from django.db import models


class AlreadyUploadedImage(models.Model):

    name = models.CharField(max_length=50, unique=True)
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
    def url(self):
        return self.image.url



