import datetime
from uuid import UUID
import cv2
from django.contrib.auth.models import AbstractUser
from django.core.files.uploadedfile import TemporaryUploadedFile
from django.core.validators import FileExtensionValidator
from django.db.models import FileField, Model, TextChoices, CharField, TimeField, F, Func, DurationField, TextField, \
    IPAddressField
from django.db.models.fields import UUIDField


class GenRandomUUID(Func):
    """
    Represents the PostgreSQL gen_random_uuid() function.
    """
    function = "gen_random_uuid"
    template = "%(function)s()"  # no args
    output_field = UUIDField()


class UUIDBaseModel(Model):
    id = UUIDField(primary_key=True, db_default=GenRandomUUID(), editable=False)

    class Meta:
        abstract = True
        required_db_vendor = 'postgresql'


class User(AbstractUser, UUIDBaseModel):
    class Language(TextChoices):
        ENG = 'en', 'English'
        RUS = 'ru', 'Russian'
        UZB = 'uz', 'Uzbek'

    username = None
    phone = CharField(max_length=11, null=True, unique=True)
    about = TextField(null=True, blank=True)
    language = CharField(max_length=5, choices=Language.choices, default=Language.ENG)
    ip_address = IPAddressField(null=True, blank=True)

    USERNAME_FIELD = 'email'


# TODO user default da is_active false boladi


class Video(UUIDBaseModel):
    class Type(TextChoices):
        PUBLIC = 'public', 'Public'
        PRIVATE = 'private', 'Private'

    file = FileField(upload_to='videos/', validators=[FileExtensionValidator(['mp4'])])
    duration = DurationField()
    type = CharField(max_length=10, choices=Type.choices, default=Type.PUBLIC)
    code = CharField(max_length=10, unique=True)

    def get_video_duration(self):
        video = cv2.VideoCapture(self.file.file.temporary_file_path())
        frames = video.get(cv2.CAP_PROP_FRAME_COUNT)
        fps = video.get(cv2.CAP_PROP_FPS)
        if not fps:
            return datetime.timedelta(seconds=0)

        seconds = round(frames / fps)
        m = seconds // 60
        video.release()
        return datetime.timedelta(minutes=m, seconds=seconds - m * 60)

    def check_video_duration(self):
        if not isinstance(self.pk, UUID):
            self.duration = self.get_video_duration()
        else:
            video = Video.objects.get(pk=self.pk)
            if self.file.name != video.file.name:
                self.duration = self.get_video_duration()

    def save(self, *, force_insert=False, force_update=False, using=None, update_fields=None):
        self.check_video_duration()
        super().save(force_insert=force_insert, force_update=force_update, using=using, update_fields=update_fields)
