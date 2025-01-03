from django.urls import path, include
from django.contrib.staticfiles.urls import static
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.conf import settings
from . import views
from django.views.decorators.http import require_POST

urlpatterns = [
    path('api/upload_image/', views.UploadImage.as_view({"get":"list", "post":"create"}), name='upload_image'),
    path('api/image_process/<str:id>/<str:label>', views.ImageProcess.as_view(), name='image_process'),

] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

urlpatterns += staticfiles_urlpatterns()
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)