from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import status
from .models import Document, Annotation
from .serializers import DocumentSerializer, AnnotationSerializer


@api_view(['GET'])
def document_list(request, pk=None):
    """
    Returns a list of documents, or a single document if pk is specified
    """
    try:
        if pk:
            document = Document.objects.get(pk=pk)
            serializer = DocumentSerializer(document)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            documents = Document.objects.all()
            serializer = DocumentSerializer(documents, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
    except Document.DoesNotExist:
        return Response({'detail': 'Document not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'detail': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
def document_create(request):
    """
    Creates a new document
    """
    serializer = DocumentSerializer(data=request.data)
    if serializer.is_valid():
        document = serializer.save()
        document_uuid = document.id
        return Response({'uuid': str(document_uuid)}, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def create_annotation_for_document(request):
    """
    Creates an annotation associated with a document using the document's UUID
    """
    try:
        document_uuid = request.data.get('document_uuid')
        document = Document.objects.get(id=document_uuid)
    except Document.DoesNotExist:
        return Response({'detail': 'Document not found'}, status=status.HTTP_404_NOT_FOUND)

    annotations_data = request.data.get('annotations', [])
    serializer_instances = []
    for annotation_data in annotations_data:
        serializer = AnnotationSerializer(data=annotation_data)
        if serializer.is_valid():
            serializer_instances.append(serializer)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    for serializer in serializer_instances:
        serializer.save(document=document)
    return Response("Annotations created successfully", status=status.HTTP_201_CREATED)


@api_view(['DELETE'])
def delete_document_annotations(request, pk):
    """
    Deletes all annotations associated with a document
    """
    try:
        document = Document.objects.get(pk=pk)
        annotations = Annotation.objects.filter(document=document)
        annotations.delete()
        return Response("Annotations deleted successfully", status=status.HTTP_200_OK)
    except Document.DoesNotExist:
        return Response({'detail': 'Document not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'detail': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def get_merged_annotations_for_book(request, book_uuid):
    """
    Retrieve annotations for a book and merge consecutive annotations with same label
    """
    try:
        annotations = Annotation.objects.filter(document_id=book_uuid).order_by('start', 'end', 'label')
        merged_annotations = []

        # Initialize variables to track consecutive annotations
        current_annotation = None
        consecutive_annotations = []

        for annotation in annotations:
            if current_annotation and annotation.start == current_annotation.end + 1 and annotation.label == current_annotation.label:
                # Consecutive annotation found, merge with the current sequence
                consecutive_annotations.append(annotation)
                current_annotation = annotation
            else:
                if len(consecutive_annotations) > 0:
                    # Merge consecutive annotations
                    merged_word = ' '.join([a.word for a in consecutive_annotations])
                    merged_annotation = {
                        'start': consecutive_annotations[0].start,
                        'end': consecutive_annotations[-1].end,
                        'word': merged_word,
                        'label': consecutive_annotations[0].label
                    }
                    merged_annotations.append(merged_annotation)
                    consecutive_annotations = []

                # Start a new sequence
                consecutive_annotations.append(annotation)
                current_annotation = annotation

        # Check if there are remaining consecutive annotations to merge
        if len(consecutive_annotations) > 0:
            merged_word = ' '.join([a.word for a in consecutive_annotations])
            merged_annotation = {
                'start': consecutive_annotations[0].start,
                'end': consecutive_annotations[-1].end,
                'word': merged_word,
                'label': consecutive_annotations[0].label
            }
            merged_annotations.append(merged_annotation)

        return Response(merged_annotations, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({'detail': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
