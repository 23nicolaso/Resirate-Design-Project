from django.db import IntegrityError, models, transaction


class BuildingManager(models.Manager):
    def from_address(self, data):
        """Find or create a building from verified address data."""
        key = "bin:" + data["building_id"] if data["building_id"] else "gid:" + data["provider_id"]
        try:
            with transaction.atomic():
                existing = self.filter(geosearch_key=key).first()
                if existing:
                    return existing, False
                existing = self.select_for_update().filter(
                    address__iexact=data["address"], borough__iexact=data["borough"],
                    geosearch_key__isnull=True,
                ).first()
                if existing:
                    existing.geosearch_key = key
                    existing.save(update_fields=["geosearch_key"])
                    return existing, False
                return self.get_or_create(geosearch_key=key, defaults={
                    "address": data["address"], "borough": data["borough"],
                    "zip_code": data["zip_code"],
                })
        except IntegrityError:
            existing = self.filter(geosearch_key=key).first()
            if existing is None:
                raise
            return existing, False


class Building(models.Model):
    objects = BuildingManager()

    geosearch_key = models.CharField(max_length=255, unique=True, null=True, blank=True)
    address = models.CharField(max_length=255, db_index=True)
    borough = models.CharField(max_length=50)
    zip_code = models.CharField(max_length=5)

    class Meta:
        ordering = ["address"]

    def __str__(self):
        return f"{self.address}, {self.borough}"