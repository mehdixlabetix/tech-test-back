from rest_framework import serializers
from .models import Document, Annotation


class DocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Document
        fields = '__all__'


class AnnotationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Annotation
        exclude = ('id','document')

    def create(self, validated_data):
        return Annotation.objects.create(**validated_data)