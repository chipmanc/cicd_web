from django.contrib import admin

from scm import models

admin.site.register(models.Repo)
admin.site.register(models.Branch)
