from django.contrib import admin

from .models import CustomUser, PulleyDetection,profile,DetectionRecord



@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('id', 'email', 'username', 'employee_id', 'is_staff', 'is_active', 'date_joined')
    list_filter = ('is_staff', 'is_active')
    search_fields = ('email', 'username', 'employee_id')
@admin.register(PulleyDetection)
class PulleyDetectionAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'uploaded_image', 'result_image', 'distances', 'created_at')
    list_filter = ('created_at', 'user')
    search_fields = ('user__email', 'distances')



@admin.register(profile)
class profileAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'profile_photo','mobile_number','address')
    search_fields = ('user__email',)
    
    
    
@admin.register(DetectionRecord)
class DetectionRecordAdmin(admin.ModelAdmin):
    list_display = ('timestamp', 'pulley_count', 'total', 'loss_mm', 'temperature_c', 'image_path')
    list_filter = ('timestamp', 'pulley_count', 'temperature_c')
    search_fields = ('timestamp', 'image_path')
    readonly_fields = ('timestamp', 'image_path')
    ordering = ('-timestamp',)
    
    fieldsets = (
        ('Timestamp', {
            'fields': ('timestamp',)
        }),
        ('Distance Measurements (mm)', {
            'fields': ('dist12', 'dist23', 'total')
        }),
        ('Expected Values (mm)', {
            'fields': ('expected_total', 'expected_dist12', 'expected_dist23')
        }),
        ('Analysis', {
            'fields': ('loss_mm', 'pulley_count', 'temperature_c', 'points_json')
        }),
    )
