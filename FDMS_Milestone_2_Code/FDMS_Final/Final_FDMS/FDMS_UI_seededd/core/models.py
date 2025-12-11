from django.conf import settings
from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User


class Location(models.Model):
    """
    Simple Location model for dropdowns and filtering.
    """
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name


class Donation(models.Model):
    STATUS_CHOICES = [
        ("available", "Available"),
        ("claimed", "Claimed"),
    ]

    title = models.CharField(max_length=255)

    # location is a FK to Location to support select_related/filters
    location = models.ForeignKey(
        Location,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="donations",
    )

    address = models.CharField(max_length=500, blank=True, null=True)

    # quantity fields
    initial_quantity = models.PositiveIntegerField()
    available_quantity = models.PositiveIntegerField(blank=True, null=True)
    deleted_quantity = models.PositiveIntegerField(default=0)  # <--- store remaining quantity
    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)
    deleted_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name='deleted_donations')
    # other metadata
    expiry_date = models.DateTimeField(blank=True, null=True)
    donation_type = models.CharField(max_length=50, blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="available")

    # relations
    donor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="donations",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    claimed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="claimed_donations",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )

    # timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # --- Soft-delete fields ---
    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)
    deleted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="deleted_donations",
    )

    def __str__(self):
        return f"{self.title} ({self.status})"

    def is_expired(self):
        """Return True if donation has an expiry_date and it is in the past."""
        if not self.expiry_date:
            return False
        return timezone.now() > self.expiry_date

    
    # Add this method
    def soft_delete_remaining(self, user=None):
    # If no quantity left
        if self.available_quantity <= 0:
            self.is_deleted = True
            self.deleted_at = timezone.now()
            if user:
                self.deleted_by = user
            self.deleted_quantity = 0
            self.save(update_fields=['is_deleted', 'deleted_at', 'deleted_by', 'deleted_quantity'])
            return

    # Keep available_quantity AS IS (do NOT set to zero)
        self.deleted_quantity = self.available_quantity   # store remaining quantity
        # DO NOT SET available_quantity = 0

        self.status = 'claimed' if self.claims.exists() else 'deleted'
        self.is_deleted = True
        self.deleted_at = timezone.now()
        if user:
            self.deleted_by = user

        self.save(update_fields=[
            'available_quantity',
            'deleted_quantity',
            'status',
            'is_deleted',
            'deleted_at',
            'deleted_by'
        ])

    @property
    def deleted_quantity_prop(self):
    # Return stored deleted quantity
        return self.deleted_quantity or 0
    deleted_quantity = models.PositiveIntegerField(default=0)
    def soft_delete(self, user=None):
   
        if self.available_quantity is None:
            self.available_quantity = 0

    # Keep remaining quantity in available_quantity instead of zero
        remaining_qty = self.available_quantity

        self.deleted_quantity = remaining_qty  # store original remaining quantity
        # available_quantity remains as the remaining quantity
        self.status = 'claimed' if self.claims.exists() else 'deleted'
        self.is_deleted = True
        self.deleted_at = timezone.now()
        if user is not None:
            self.deleted_by = user

        self.save(update_fields=['available_quantity', 'deleted_quantity', 'status', 'is_deleted', 'deleted_at', 'deleted_by'])

    def save(self, *args, **kwargs):
        if self._state.adding and self.available_quantity is None:
            self.available_quantity = self.initial_quantity
        super().save(*args, **kwargs)


    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Donation"
        verbose_name_plural = "Donations"


class Claim(models.Model):
    """
    Tracks each claim action (who claimed how many units from which donation).
    """
    donation = models.ForeignKey(Donation, related_name="claims", on_delete=models.CASCADE)
    claimer = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="claims", on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.claimer} claimed {self.quantity} of {self.donation.title}"
