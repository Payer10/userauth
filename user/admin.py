from django.contrib import admin
from .models import User, VarificationCode


@admin.register(User)
class UserAdmin(admin.ModelAdmin):  
    list_display = ('email', 'is_active', 'is_verified', 'role', 'created_at')
    search_fields = ('email', 'username')
    list_filter = ('is_active', 'is_verified', 'role')
    ordering = ('created_at',)


@admin.register(VarificationCode)
class VarificationCodeAdmin(admin.ModelAdmin):
    list_display = ('user', 'code', 'purpose', 'created_at', 'expired_at')
    search_fields = ('user__email', 'code', 'purpose')
    list_filter = ('purpose', 'created_at', 'expired_at')
    ordering = ('-created_at',)
