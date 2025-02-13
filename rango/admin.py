from django.contrib import admin
from rango.models import Category, Page 
from rango.models import UserProfile

# Register your models here.

class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug':('name',)}

#update registration to include customized interface
admin.site.register(Category, CategoryAdmin) 





class PageAdmin(admin.ModelAdmin):
    list_display = ('title','category','url')

admin.site.register(Page, PageAdmin)


# register UserProfile model with the admin interface here 

admin.site.register(UserProfile) 

