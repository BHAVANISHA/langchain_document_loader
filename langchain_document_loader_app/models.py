from django.db import models


class UploadedFile( models.Model ):
    file_upload = models.FileField()


