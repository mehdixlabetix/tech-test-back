from django.db import models
import uuid
# Create your models here.


class Document(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=100)
    content = models.TextField()


class Annotation(models.Model):
    id = models.AutoField(primary_key=True)  # Auto-incrementing integer field
    document = models.ForeignKey(Document, on_delete=models.CASCADE)
    word = models.CharField(max_length=100)
    label = models.CharField(max_length=50)
    start = models.IntegerField()
    end = models.IntegerField()
