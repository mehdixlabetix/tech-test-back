from django.urls import path
from . import views

urlpatterns = [
    path('documents/', views.document_list, name='document-list'), #list all docuements
    path('documents/<uuid:pk>/', views.document_list, name='single-document'), #list one document
    path('document/', views.document_create, name='document-create'),#create a document
    path('annotation/', views.create_annotation_for_document, name='create-annotation'),#create an annotation for a book
    path('annotations/<uuid:book_uuid>/', views.get_merged_annotations_for_book, name='get-annotations-for-book'),#get annotations for a book
    path('documents/<uuid:pk>/annotations/', views.delete_document_annotations, name='delete_document_annotations'),]