from django.contrib import admin

from user.models import User

from django.contrib.auth.admin import UserAdmin  # 从django继承过来后进行定制
from django.contrib.auth.forms import UserCreationForm, UserChangeForm  # admin中涉及到的两个表单


class CustomUserAdmin(UserAdmin):
    def __init__(self, *args, **kwargs):
        super(CustomUserAdmin, self).__init__(*args, **kwargs)
        self.list_display = ('username', 'is_active', 'is_superuser', 'last_login', 'date_joined')
        self.search_fields = ('username', )
        self.form = UserChangeForm  # 编辑用户表单，使用自定义的表单
        self.add_form = UserCreationForm  # 添加用户表单，使用自定义的表单

    def changelist_view(self, request, extra_context=None):
        if not request.user.is_superuser:
            self.fieldsets = ((None, {'fields': ('username', 'password',)}),
                              # (_('Permissions'), {'fields': ('is_active', )}),
                              # (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
                              )
            self.add_fieldsets = ((None, {'classes': ('wide',),
                                          'fields': ('username', 'password1', 'password2', 'is_active'),
                                          }),
                                  )
        else:
            self.fieldsets = ((None, {'fields': ('username', 'password',)}),
                              # (_('Permissions'), {'fields': ('is_active', 'is_superuser')}),
                              # (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
                              )
            self.add_fieldsets = ((None, {'classes': ('wide',),
                                          'fields': ('username', 'password1', 'password2', 'is_active', 'is_superuser'),
                                          }),
                                  )
        return super(CustomUserAdmin, self).changelist_view(request, extra_context)


admin.site.register(User, CustomUserAdmin)  # 注册
