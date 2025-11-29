from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils import timezone




class CustomUserManager(BaseUserManager):
    def create_user(self, email, username, employee_id, password=None):
        if not email:
            raise ValueError('Users must have an email address')
        if not username:
            raise ValueError('Users must have a username')
        if not employee_id:
            raise ValueError('Users must have an employee ID')

        email = self.normalize_email(email)
        user = self.model(email=email, username=username, employee_id=employee_id)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, username, employee_id, password=None):
        user = self.create_user(email, username, employee_id, password)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user


class CustomUser(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(max_length=50, unique=True)
    email = models.EmailField(unique=True)
    employee_id = models.CharField(max_length=20, unique=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)
    # your_phonto = models.ImageField(upload_to='profile_photos/', null=True, blank=True) 
    last_login = models.DateTimeField(auto_now=True)
    

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'employee_id']

    objects = CustomUserManager()

    def __str__(self):
        return self.username



from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class PulleyDetection(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, blank=True, null=True)
    uploaded_image = models.ImageField(upload_to='uploads/')
    result_image = models.ImageField(upload_to='results/')
    temperature_c = models.FloatField(blank=True, null=True)
    htl_value = models.FloatField(blank=True, null=True)
    dist_p1_p2 = models.FloatField(blank=True, null=True)
    dist_p2_p3 = models.FloatField(blank=True, null=True)
    total_distance = models.FloatField(blank=True, null=True)
    expected_total = models.FloatField(blank=True, null=True)
    loss_mm = models.FloatField(blank=True, null=True)
    distances = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Pulley Detection {self.id} - {self.created_at.strftime('%Y-%m-%d %H:%M:%S')}"


class profile(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    profile_photo = models.ImageField(upload_to='profile_photos/')
    mobile_number = models.CharField(max_length=10, blank=True, null=True)
    address = models.CharField(max_length=300,blank=True, null=True)

    def __str__(self):
        return f"Profile of {self.user.username}"
# Create your models here.

class DetectionRecord(models.Model):
    """Model to store camera detection data"""
    # user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(default=timezone.now, db_index=True)
    
    # Distance measurements (in mm)
    dist12 = models.FloatField(null=True, blank=True, help_text="Distance between pulley 1 and 2 (mm)")
    dist23 = models.FloatField(null=True, blank=True, help_text="Distance between pulley 2 and 3 (mm)")
    total = models.FloatField(null=True, blank=True, help_text="Total distance P1->P3 (mm)")
    
    # Expected values
    expected_total = models.FloatField(null=True, blank=True, help_text="Expected total distance (mm)")
    expected_dist12 = models.FloatField(null=True, blank=True, help_text="Expected distance P1->P2 (mm)")
    expected_dist23 = models.FloatField(null=True, blank=True, help_text="Expected distance P2->P3 (mm)")
    
    # Loss calculation
    loss_mm = models.FloatField(null=True, blank=True, help_text="Loss vs expected (mm)")
    
    # Detection info
    pulley_count = models.IntegerField(default=0, help_text="Number of pulleys detected")
    temperature_c = models.FloatField(null=True, blank=True, help_text="Temperature in Celsius")
    
    # Points data (stored as JSON-like format)
    points_json = models.TextField(null=True, blank=True, help_text="Pulley center points")
    image_path = models.ImageField(
        upload_to='best_captures/',
        null=True,
        blank=True,
        help_text="Saved annotated image file"
    )
    
    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['-timestamp']),
        ]
    
    def __str__(self):
        return f"Detection at {self.timestamp.strftime('%Y-%m-%d %H:%M:%S')} - {self.pulley_count} pulleys"
