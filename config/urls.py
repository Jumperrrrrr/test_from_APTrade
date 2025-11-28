from django.contrib import admin
from django.urls import path
from django.views.generic import TemplateView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', TemplateView.as_view(template_name='index.html'), name='home'),
    path('page1/', TemplateView.as_view(template_name='page1.html'), name='page1'),
    path('page1/sub1/', TemplateView.as_view(template_name='page1.html'), name='page1_sub1'),
    path('page1/sub2/', TemplateView.as_view(template_name='page1.html'), name='page1_sub2'),
    path('page2/', TemplateView.as_view(template_name='page2.html'), name='page2'),
    path('page2/sub1/', TemplateView.as_view(template_name='page2.html'), name='page2_sub1'),
    path('page3/', TemplateView.as_view(template_name='page3.html'), name='page3'),
    path('category/<int:pk>/', TemplateView.as_view(template_name='category.html'), name='category'),
]
