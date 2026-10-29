from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    """A registered ResiRate account."""

    def __str__(self):
        return self.username