from django.db import models


class Building(models.Model):
    address = models.CharField(max_length=255, db_index=True)
    borough = models.CharField(max_length=50)
    zip_code = models.CharField(max_length=5)

    class Meta:
        ordering = ["address"]

    def __str__(self):
        return f"{self.address}, {self.borough}"