# documents/urls.py
"""
Documents app URLs. Include this in project urls as:
    path('api/', include('documents.urls'))
"""

from django.urls import path
from .api.list import DocumentListAPIView
from .api.add import AddDocumentAPIView
from .api.detail import DocumentDetailAPIView


# Simple dispatcher: GET -> list, POST -> add for the same path
def documents_root_dispatcher(request, *args, **kwargs):
    if request.method == 'GET':
        return DocumentListAPIView.as_view()(request, *args, **kwargs)
    if request.method == 'POST':
        return AddDocumentAPIView.as_view()(request, *args, **kwargs)
    from django.http import HttpResponseNotAllowed
    return HttpResponseNotAllowed(['GET', 'POST'])


urlpatterns = [
    path('documents/', documents_root_dispatcher, name='documents-root'),
    path('documents/<uuid:id>/', DocumentDetailAPIView.as_view(), name='document-detail'),
]

