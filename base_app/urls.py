from django.urls import path
from .views import IndexView, TestDetailView, TestCheckerView,render_pdf_view

urlpatterns = [
    path("", IndexView.as_view(), name='index'),
    path("stage/<int:pk>/", TestDetailView.as_view(), name='test'),
    path("check_stage_test/", TestCheckerView, name='checker'),
    path("print/", render_pdf_view, name='print'),

]
