from django.urls import path
from .views import *

urlpatterns = [
    path('merge-pdf/', MergePDFView.as_view(), name='merge_pdf'),
    path('split-pdf/', SplitPDFView.as_view(), name='split_pdf'),
    path('split-pdf-by-page/', SplitPDFByPageView.as_view(), name='split_pdf_by_page'),
    path('encrypt-pdf/', EncryptPDFView.as_view(), name='encrypt_pdf'),
    path('ocr-pdf/', OCRPDFView.as_view(), name='ocr_pdf'),
]