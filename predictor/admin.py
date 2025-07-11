# from django.contrib import admin

# # Register your models here.
# from .models import SkinCondition

# admin.site.register(SkinCondition)


from django.contrib import admin
from .models import SkinCondition, Remedy,SkinCondition_page
from .models import Article



class RemedyInline(admin.TabularInline):
    model = Remedy
    extra = 3  # Display space for 3 remedies
    fields = ('title', 'image', 'image_preview', 'amount', 'directions')  # Updated fields
    readonly_fields = ('image_preview',)  # Make preview read-only
    
    def image_preview(self, obj):
        return obj.image_preview()
    
    image_preview.short_description = 'Preview'
    
class SkinConditionAdmin(admin.ModelAdmin):
    inlines = [RemedyInline]
    list_display = ('name',)
    search_fields = ('name',)

admin.site.register(SkinCondition, SkinConditionAdmin)
admin.site.register(SkinCondition_page)

@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'published_date')
    prepopulated_fields = {'slug': ('title',)}
    search_fields = ('title', 'content')
    list_filter = ('category', 'is_featured')