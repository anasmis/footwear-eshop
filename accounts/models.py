from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver


class Profile(models.Model):
    """Informations complémentaires du client, liées au User Django."""

    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="profile"
    )
    phone = models.CharField("Téléphone", max_length=30, blank=True)
    address = models.CharField("Adresse", max_length=255, blank=True)
    city = models.CharField("Ville", max_length=100, blank=True)
    postal_code = models.CharField("Code postal", max_length=20, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Profil client"
        verbose_name_plural = "Profils clients"

    def __str__(self):
        return f"Profil de {self.user.username}"


@receiver(post_save, sender=User)
def create_or_update_profile(sender, instance, created, raw=False, **kwargs):
    """Crée automatiquement un profil à la création d'un utilisateur.

    On ignore le chargement de fixtures (raw=True, ex. loaddata) : le profil
    réel est alors chargé tel quel depuis le dump, sans doublon.
    """
    if raw:
        return
    if created:
        Profile.objects.create(user=instance)
    else:
        Profile.objects.get_or_create(user=instance)
