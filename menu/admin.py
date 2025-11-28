from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse, NoReverseMatch
from .models import Menu, MenuItem


class MenuItemInline(admin.TabularInline):
    model = MenuItem
    extra = 0
    fields = ('title', 'parent', 'url', 'named_url', 'order')
    fk_name = 'menu'
    
    def get_formset(self, request, obj=None, **kwargs):
        formset = super().get_formset(request, obj, **kwargs)
        
        if obj and obj.pk:
            original_form = formset.form
            
            class CustomForm(original_form):
                def __init__(self, *args, **kwargs):
                    super().__init__(*args, **kwargs)
                    if 'parent' in self.fields:
                        self.fields['parent'].queryset = MenuItem.objects.filter(menu=obj)
            
            formset.form = CustomForm
        
        return formset


@admin.register(Menu)
class MenuAdmin(admin.ModelAdmin):
    list_display = ('name', 'items_count')
    inlines = [MenuItemInline]
    
    def items_count(self, obj):
        return obj.items.count()
    items_count.short_description = 'Количество пунктов'


@admin.register(MenuItem)
class MenuItemAdmin(admin.ModelAdmin):
    list_display = ('title', 'menu', 'parent', 'url_display', 'order')
    list_filter = ('menu', 'parent')
    search_fields = ('title', 'url', 'named_url')
    fields = ('menu', 'title', 'parent', 'url', 'named_url', 'order')
    
    def url_display(self, obj):
        url = obj.get_url()
        if url and url != '#':
            return format_html('<a href="{}" target="_blank">{}</a>', url, url)
        return '-'
    url_display.short_description = 'URL'
    
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        
        if 'parent' in form.base_fields:
            if obj and obj.pk and obj.menu:
                exclude_ids = [obj.id]
                def get_descendants(item_id):
                    descendants = []
                    children = MenuItem.objects.filter(parent_id=item_id)
                    for child in children:
                        descendants.append(child.id)
                        descendants.extend(get_descendants(child.id))
                    return descendants
                
                exclude_ids.extend(get_descendants(obj.id))
                form.base_fields['parent'].queryset = MenuItem.objects.filter(menu=obj.menu).exclude(id__in=exclude_ids)
            elif obj and hasattr(obj, 'menu') and obj.menu:
                form.base_fields['parent'].queryset = MenuItem.objects.filter(menu=obj.menu)
            else:
                form.base_fields['parent'].queryset = MenuItem.objects.none()
        
        return form
    
    def save_model(self, request, obj, form, change):
        if obj.parent and not obj.menu:
            obj.menu = obj.parent.menu
        elif obj.parent and obj.parent.menu != obj.menu:
            obj.menu = obj.parent.menu
        
        super().save_model(request, obj, form, change)
