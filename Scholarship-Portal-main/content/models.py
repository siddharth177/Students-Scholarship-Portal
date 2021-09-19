from django.core.validators import FileExtensionValidator
from django.db import models
from accounts.models import CustomUser
from django.template.defaultfilters import slugify
from django.utils.text import slugify

def get_pdf_path(instance, filename):
    return 'Attached_files/{0}/pdf/{1}'.format(instance.app_id, filename)


class Application_Count(models.Model):
    app_cnt = models.IntegerField(default=0)

    def __unicode__(self):
        return str(self.app_cnt)


class Scholarship(models.Model):
    name = models.CharField(max_length=255, default='')
    # slug = models.SlugField(max_length=30, unique=True, editable=False)
    abbreviation = models.CharField(max_length=10, default='')
    department = models.ForeignKey('accounts.Department', verbose_name="Department", on_delete=models.CASCADE, blank=True,
                                   null=True)
    requirements_info = models.TextField(default='Requirement information needs to be updated.')
    
    caste = models.CharField(max_length=255, default='NA')
    program = models.CharField(max_length=255, default='NA')
    specialization = models.CharField(max_length=255, default='NA')
    gender = models.CharField(max_length=255, default='NA')
    minimum_cgpa = models.IntegerField(max_length=255, default='0')

    external_link = models.CharField(max_length=1000, default='NA')

    def __str__(self):
        return self.name


class Application(models.Model):
    app_id = models.CharField(max_length=20, primary_key=True)
    request = models.ForeignKey(Scholarship, verbose_name="Request", on_delete=models.CASCADE,default=1)
    applicant = models.ForeignKey(CustomUser, verbose_name="Applicant", on_delete=models.CASCADE,default=1)
    category = models.CharField(max_length=300, default="")
    title = models.CharField(max_length=300, default="")
    department = models.ForeignKey('accounts.Department', verbose_name="Department", on_delete=models.CASCADE, blank=True,
                                   null=True)

    attached_pdf = models.FileField(upload_to=get_pdf_path,
                                   validators=[FileExtensionValidator(["pdf"])],
                                   null=True, blank=True, default=None)

    is_approved = models.BooleanField(default=False)
    is_rejected = models.BooleanField(default=False)
    def __unicode__(self):
        return str(self.app_id)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.category)
        super(Application, self).save(*args, **kwargs)


