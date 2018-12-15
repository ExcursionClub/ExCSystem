import setup_django

from core.models.FileModels import AlreadyUploadedImage
from core.models.GearModels import Gear


DEFAULT_IMAGE_PK = 0
SHAKA_IMAGE_PK = 1


shaka_img = AlreadyUploadedImage.objects.get(pk=SHAKA_IMAGE_PK)
print(shaka_img)

for gear in Gear.objects.filter(DEFAULT_IMAGE_PK):

    print(gear)

    gear.image = shaka_img
    gear.save()

