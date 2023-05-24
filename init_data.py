# coding: utf-8
"""项目初始化脚本"""

import os

import django
import shutil

from django.db.transaction import atomic

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mcs.settings")
django.setup()

from user.models import User, Permissions

permission_data = [

    {'id': 1, 'code': 'personnels', 'name': '用户管理', 'parent_id': None, 'category_name': '系统管理'},
    {'id': 2, 'code': 'view_personnels', 'name': '查看', 'parent_id': 1},
    {'id': 3, 'code': 'add_personnels', 'name': '新增', 'parent_id': 1},
    {'id': 4, 'code': 'change_personnels', 'name': '修改', 'parent_id': 1},
    {'id': 5, 'code': 'update_personnels', 'name': '启用/停用', 'parent_id': 1},
    {'id': 6, 'code': 'delete_personnels', 'name': '删除', 'parent_id': 1},
    {'id': 7, 'code': 'export_personnels', 'name': '导出', 'parent_id': 1},
    {'id': 8, 'code': 'import_personnels', 'name': '导入', 'parent_id': 1},

    {'id': 9, 'code': 'group_extension', 'name': '角色管理', 'parent_id': None, 'category_name': '系统管理'},
    {'id': 10, 'code': 'view_group_extension', 'name': '查看', 'parent_id': 9},
    {'id': 11, 'code': 'add_group_extension', 'name': '新增', 'parent_id': 9},
    {'id': 12, 'code': 'change_group_extension', 'name': '修改', 'parent_id': 9},
    {'id': 13, 'code': 'update_group_extension', 'name': '启用/停用', 'parent_id': 9},
    {'id': 14, 'code': 'delete_group_extension', 'name': '删除', 'parent_id': 9},

    {'id': 15, 'code': 'department', 'name': '人员组织架构', 'parent_id': None, 'category_name': '系统管理'},
    {'id': 16, 'code': 'view_department', 'name': '查看', 'parent_id': 15},

    {'id': 17, 'code': 'material', 'name': '物料信息查询', 'parent_id': None, 'category_name': '物料信息查询'},
    {'id': 18, 'code': 'view_material', 'name': '查看', 'parent_id': 17},
    {'id': 19, 'code': 'export_material', 'name': '导入', 'parent_id': 17},
    {'id': 20, 'code': 'add_material', 'name': '物料信息显示设定', 'parent_id': 17},
    {'id': 21, 'code': 'multi_material', 'name': '批量查询', 'parent_id': 17},

    {'id': 22, 'code': 'user_operation_log', 'name': '操作日志查询', 'parent_id': None, 'category_name': '系统管理'},
    {'id': 23, 'code': 'view_user_operation_log', 'name': '查看', 'parent_id': 22},

    {'id': 24, 'code': 'problem', 'name': '项目问题点管理', 'parent_id': None, 'category_name': '项目问题点管理'},
    {'id': 25, 'code': 'view_problem', 'name': '查看', 'parent_id': 24},
    {'id': 26, 'code': 'import_problem', 'name': '导入', 'parent_id': 24},
    {'id': 27, 'code': 'add_problem', 'name': '新建', 'parent_id': 24},
    {'id': 28, 'code': 'change_problem', 'name': '编辑', 'parent_id': 24},
    {'id': 29, 'code': 'export_problem', 'name': '导出', 'parent_id': 24},

    # 下一个开始: 30

]


@atomic()
def init_permissions():
    for item in permission_data:
        Permissions.objects.create(**item)


def main():
    print('开始迁移数据库')
    apps = ('agv', 'basics', 'user', 'monitor')

    for app in apps:
        try:
            shutil.rmtree(f"{app}/migrations")
        except Exception:
            pass

    os.system(
        'python manage.py makemigrations {}'.format(
            ' '.join(apps)
        ))
    os.system('python manage.py migrate')

    print('创建超级管理员...')
    User.objects.create_superuser('gzmcs123', '123456@qq.com', '123456')
    init_permissions()


if __name__ == '__main__':
    main()
