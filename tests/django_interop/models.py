"""
Kitchen sink model for a pet sitting business,
generated by Claude.
"""

import uuid
from decimal import Decimal

from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils import timezone


class PetSittingGig(models.Model):
    """
    A comprehensive model for a pet sitting business that somehow needs
    to track an absurd amount of information about each gig.
    """

    # Basic identification
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    gig_number = models.AutoField(unique=True, help_text="Auto-incrementing gig number")

    # Text fields of various sizes
    pet_name = models.CharField(max_length=100, help_text="What do we call this furry overlord?")
    pet_nickname = models.CharField(max_length=50, blank=True, help_text="Their street name")
    owner_notes = models.TextField(blank=True, help_text="Novel-length instructions from neurotic pet parents")
    emergency_contact_info = models.TextField(help_text="When things go sideways")
    secret_treat_hiding_spots = models.TextField(blank=True, help_text="Where the good stuff is stashed")

    # Email and URL fields
    owner_email = models.EmailField(help_text="For sending cute pet pics")
    pet_instagram = models.URLField(blank=True, help_text="Because of course they have one")
    vet_website = models.URLField(blank=True, help_text="Dr. Whiskers' online presence")

    # File and image fields
    pet_photo = models.ImageField(upload_to="pet_photos/", blank=True, help_text="Mugshot for identification")
    vaccination_records = models.FileField(upload_to="documents/", blank=True, help_text="Proof of shots")
    house_key_photo = models.ImageField(upload_to="keys/", blank=True, help_text="Which key opens what")

    # Numeric fields
    daily_rate = models.DecimalField(max_digits=8, decimal_places=2, help_text="What this chaos costs")
    pet_weight = models.FloatField(validators=[MinValueValidator(0.1)], help_text="In pounds (for dosing purposes)")
    number_of_pets = models.PositiveIntegerField(default=1, help_text="Size of the furry army")
    owner_anxiety_level = models.SmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(10)],
        help_text="Scale of 1-10, where 10 is 'calls every hour'",
    )
    house_alarm_code = models.PositiveIntegerField(blank=True, null=True, help_text="Please don't set this off")

    # Date and time fields
    start_date = models.DateField(help_text="When the adventure begins")
    end_date = models.DateField(help_text="When freedom returns")
    start_time = models.TimeField(help_text="Exact moment of responsibility transfer")
    last_fed = models.DateTimeField(blank=True, null=True, help_text="When they last conned someone into food")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Duration field
    typical_walk_duration = models.DurationField(help_text="How long they drag you around the block")

    # Boolean fields
    is_house_trained = models.BooleanField(default=True, help_text="Are we dealing with surprises?")
    needs_medication = models.BooleanField(default=False, help_text="Am I now a pet pharmacist?")
    is_escape_artist = models.BooleanField(default=False, help_text="Houdini tendencies?")
    owner_has_security_cameras = models.BooleanField(default=False, help_text="Am I being watched?")
    pet_is_social_media_famous = models.BooleanField(default=False, help_text="Do I need to maintain their brand?")

    # Choice fields
    PET_SPECIES_CHOICES = [
        ("dog", "Dog"),
        ("cat", "Cat"),
        ("bird", "Bird"),
        ("fish", "Fish"),
        ("hamster", "Hamster"),
        ("snake", "Snake"),
        ("turtle", "Turtle"),
        ("other", "Some exotic creature that requires YouTube tutorials"),
    ]
    pet_species = models.CharField(max_length=20, choices=PET_SPECIES_CHOICES)

    DIFFICULTY_CHOICES = [
        ("easy", "Easy Peasy"),
        ("moderate", "Moderate Challenge"),
        ("hard", "Advanced Pet Wrangling"),
        ("expert", "Call in the Professionals"),
        ("impossible", "May God Have Mercy on My Soul"),
    ]
    difficulty_level = models.CharField(max_length=20, choices=DIFFICULTY_CHOICES, default="easy")

    PAYMENT_STATUS_CHOICES = [
        ("pending", "Pending"),
        ("partial", "Partial Payment"),
        ("paid", "Fully Paid"),
        ("overdue", "Overdue (Send Lawyers)"),
    ]
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default="pending")

    # Foreign key relationships
    sitter = models.ForeignKey(User, on_delete=models.CASCADE, help_text="The brave soul taking this on")
    backup_sitter = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="backup_gigs",
        help_text="Emergency reinforcement",
    )

    # JSON field (for PostgreSQL)
    special_instructions = models.JSONField(
        default=dict,
        blank=True,
        help_text="Structured chaos: feeding times, quirks, emergency protocols",
    )

    # Binary field (rarely used, but hey, kitchen sink!)
    house_wifi_password = models.BinaryField(blank=True, help_text="Encrypted WiFi password")

    # IP Address field
    security_camera_ip = models.GenericIPAddressField(blank=True, null=True, help_text="For checking in remotely")

    # Slug field
    slug = models.SlugField(unique=True, help_text="URL-friendly identifier")

    class Meta:
        ordering = ["-start_date", "-start_time"]
        verbose_name = "Pet Sitting Gig"
        verbose_name_plural = "Pet Sitting Gigs"
        indexes = [
            models.Index(fields=["start_date", "end_date"]),
            models.Index(fields=["pet_species", "difficulty_level"]),
        ]

    @property
    def total_days(self) -> int:
        """Calculate the total duration of the gig"""
        return (self.end_date - self.start_date).days + 1

    @property
    def total_cost(self) -> Decimal:
        """Calculate total cost of the gig"""
        return self.daily_rate * self.total_days

    def is_current(self) -> bool:
        """Check if the gig is currently active"""
        today = timezone.now().date()
        return self.start_date <= today <= self.end_date


class PetEmergencyContact(models.Model):
    """Because pets always have drama at 3 AM"""

    gig = models.ForeignKey(PetSittingGig, on_delete=models.CASCADE, related_name="emergency_contacts")
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=20)
    relationship = models.CharField(max_length=50, help_text="Aunt, neighbor, fellow pet parent, etc.")
    availability = models.CharField(max_length=100, help_text="When they can actually help")


class PetMedication(models.Model):
    """For when pets have more prescriptions than their owners"""

    gig = models.ForeignKey(PetSittingGig, on_delete=models.CASCADE, related_name="medications")
    medication_name = models.CharField(max_length=100)
    dosage = models.CharField(max_length=50)
    frequency = models.CharField(max_length=100, help_text="How often to drug the pet")
    administration_method = models.CharField(
        max_length=100,
        help_text="Hidden in food, wrestling match, or magic trick",
    )
