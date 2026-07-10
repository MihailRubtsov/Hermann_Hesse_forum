from django.db import models
from django.contrib.auth.models import User

class Thread(models.Model):
    title = models.CharField(max_length=255, verbose_name='Thementitel')
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name='threads', verbose_name='Ersteller')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Erstellt am')

    def __str__(self):
        return self.title
    
    class Meta:
        verbose_name = "Thema"
        verbose_name_plural = "Themen"
        ordering = ['-created_at']


class Post(models.Model):
    thread = models.ForeignKey(Thread, on_delete=models.CASCADE, related_name='posts', verbose_name='Thema')
    author = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Autor')
    content = models.TextField(verbose_name='Inhalt')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Sendedatum')

    def __str__(self):
        return f"Beitrag von {self.author} in {self.thread.title}"

    class Meta:
        verbose_name = "Beitrag"
        verbose_name_plural = "Beiträge"
        ordering = ['created_at']