from django.db import models

class Project(models.Model):
    title = models.CharField(max_length=200)
    category = models.CharField(max_length=100)
    description = models.TextField()
    image = models.ImageField(upload_to='projects/', blank=True, null=True)
    project_url = models.URLField(blank=True, null=True)
    date_created = models.DateField(auto_now_add=True)

    class Meta:
        ordering = ['-date_created']

    def __str__(self):
        return self.title

class Service(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    tags = models.CharField(max_length=250, help_text="Comma-separated list of tags/technologies")

    @property
    def tag_list(self):
        if not self.tags:
            return []
        return [tag.strip() for tag in self.tags.split(',') if tag.strip()]

    def __str__(self):
        return self.title

class ContactMessage(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Message from {self.name} ({self.email}) at {self.created_at.strftime('%Y-%m-%d %H:%M')}"
