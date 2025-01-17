from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.utils import timezone
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password

class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)

        # Remove 'username' from extra_fields if it's not in the model
        extra_fields.pop('username', None)

        user = self.model(email=email, **extra_fields)
        
        if password:
            user.set_password(password)  # This is the correct method for setting the password
            
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)






class Baseuser(models.Model):
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'  # Field used as the unique identifier
    REQUIRED_FIELDS = []  # Other required fields besides `email`

    class Meta:
        verbose_name = "Base User"
        verbose_name_plural = "Base Users"

    def __str__(self):
        return self.email

    def check_password(self, raw_password):
        """Check hashed password against a raw password."""
        from django.contrib.auth.hashers import check_password
        return check_password(raw_password, self.password)

    def set_password(self, raw_password):
        """Set and hash the password."""
        self.password = make_password(raw_password)
        self.save()
        
    def has_perm(self, perm, obj=None):
        """Return True if the user has the specific permission, False otherwise."""
        # Add logic here to check for specific permissions
        return True  # Placeholder, modify based on your needs

    def has_module_perms(self, app_label):
        """Return True if the user has permissions for the given app label."""
        # Add logic here to check for module permissions
        return True  # Placeholder, modify based on your needs

    @property
    def is_authenticated(self):
        """Property to mimic `is_authenticated` for custom user models."""
        return True
    
    @property
    def is_anonymous(self):
        """Always return False for authenticated users."""
        return False


# Customer Model
class Customers(Baseuser):
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)

    class Meta:
        verbose_name = "Customer"
        verbose_name_plural = "Customers"

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


# Vendor Model
class Vendors(Baseuser):
    business_name = models.CharField(max_length=255)
    contact_number = models.CharField(max_length=15)

    class Meta:
        verbose_name = "Vendor"
        verbose_name_plural = "Vendors"

    def __str__(self):
        return self.business_name
