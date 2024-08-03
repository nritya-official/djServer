from django.db import models

# Create your models here.

class Review(models.Model):
    user_id = models.IntegerField()
    studio_id = models.IntegerField()
    rating = models.FloatField()

    def __str__(self):
        return f'Review by User {self.user_id} for Studio {self.studio_id}'