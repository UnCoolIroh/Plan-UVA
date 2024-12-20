from django.contrib import admin

# Register your models here.
from .models import *
admin.site.register(Project_user)

admin.site.register(Message)
admin.site.register(Conversation)
admin.site.register(Project_group)
admin.site.register(Document)