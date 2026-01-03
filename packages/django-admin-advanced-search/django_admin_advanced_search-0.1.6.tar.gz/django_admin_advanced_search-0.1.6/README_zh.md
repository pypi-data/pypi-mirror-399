# Django Admin 高级搜索

[![PyPI](https://img.shields.io/pypi/v/django-admin-advanced-search)](https://pypi.org/project/django-admin-advanced-search/)
[![License](https://img.shields.io/pypi/l/django-admin-advanced-search)](https://github.com/shifenhutu/django-admin-advanced-search/blob/main/LICENSE)
[![Python Version](https://img.shields.io/pypi/pyversions/django-admin-advanced-search)](https://pypi.org/project/django-admin-advanced-search/)

Django Admin 界面的高级搜索功能，可直接在搜索栏中实现强大的文本字段过滤功能。

[English README](README.md)

## 功能特性

- 增强的 Django Admin 搜索能力，支持文本字段的高级语法
- 支持字段特定搜索和多种操作符
- 支持大小写敏感和大小写不敏感的匹配选项
- 支持多个条件的AND逻辑组合
- 与现有 Django Admin 界面无缝集成
- 数据库级别的过滤实现，性能优化

## 要求

- Python >= 3.12
- Django >= 5.1

注意：此包已在 Django 5.1, 5.2 和 Python 3.12 上进行了专门测试。虽然它可能在其他版本上工作，但不保证在此范围之外的版本兼容性。

此包专为文本字段搜索而设计。对于数字和日期/时间字段的过滤，请考虑使用 [django-admin-rangefilter](https://github.com/silentsokolov/django-admin-rangefilter)。

## 安装

```bash
pip install django-admin-advanced-search
```

## 使用方法

1. 将 `django_admin_advanced_search` 添加到你的 `INSTALLED_APPS` 中：

```python
INSTALLED_APPS = [
    ...
    'django_admin_advanced_search',
    ...
]
```

2. 在你的管理类中使用高级搜索：

```python
from django.contrib import admin
from django_admin_advanced_search.mixins import AdvancedSearchMixin

class MyModelAdmin(AdvancedSearchMixin, admin.ModelAdmin):
    search_fields = ['name', 'description', 'author__name']  # 可搜索的字段
    # 你的其他管理配置

admin.site.register(MyModel, MyModelAdmin)
```

## 搜索语法

| 语法 | 描述 | 示例 | SQL 等价 |
|------|------|------|----------|
| `field:value` | 大小写不敏感包含 | `name:john` | `name ILIKE '%john%'` |
| `field:=value` | 大小写不敏感精确匹配 | `name:=john` | `name ILIKE 'john'` |
| `field:==value` | 大小写敏感精确匹配 | `name:==John` | `name = 'John'` |
| `field:!value` | 大小写敏感包含 | `name:!john` | `name LIKE '%john%'` |
| `field:*suffix` | 大小写不敏感后缀匹配 | `name:*son` | `name ILIKE '%son'` |
| `field:!*suffix` | 大小写敏感后缀匹配 | `name:!*son` | `name LIKE '%son'` |
| `field:prefix*` | 大小写不敏感前缀匹配 | `name:john*` | `name ILIKE 'john%'` |
| `field:!prefix*` | 大小写敏感前缀匹配 | `name:!john*` | `name LIKE 'john%'` |

## 组合搜索

高级搜索语法可以与普通文本搜索结合使用。当两者同时存在时，首先应用高级搜索过滤器，然后使用 Django 的默认搜索行为将普通文本搜索应用于过滤后的结果。

示例:
- `title:=Python lisa` - 查找标题精确匹配 "Python"（大小写不敏感）且在任何搜索字段中包含 "lisa" 的项目
- `lisa title:=Python` - 与上述相同，顺序无关紧要
- `title:django* tutorial` - 查找标题以 "django" 开头（大小写不敏感）且在任何搜索字段中包含 "tutorial" 的项目

## 示例

- `title:django*` - 标题以"django"开头的项目（大小写不敏感）
- `author__name:*smith` - 作者姓名以"smith"结尾的项目（大小写不敏感）
- `title:==Learning Python` - 标题精确为"Learning Python"的项目（大小写敏感）
- `title:"Python Programming"` - 标题包含精确短语"Python Programming"的项目
- `title:python author__name:john` - 标题包含"python"且作者姓名包含"john"的项目
- `title:=Python lisa` - 标题精确匹配"Python"（大小写不敏感）且在任何搜索字段中包含"lisa"的项目



## 数据库排序和性能说明

- 该包生成数据库级别的过滤器，确保最佳性能
- 对于大小写不敏感的操作，包使用数据库的原生大小写不敏感比较操作符
- 确保数据库列具有适当的排序规则设置以获得最佳性能
- 复杂的多字段搜索可能会生成复杂的 SQL 查询；考虑在经常搜索的字段上添加数据库索引
- 使用相关字段查找时（例如 `author__name:john`），确保外键关系正确建立索引

## 测试


该包使用Django内置的测试框架。运行测试的方法：

```bash
python -m django test tests --settings=tests.settings
```

## 贡献

欢迎贡献！请随时提交 Pull Request。

1. Fork 仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 打开 Pull Request

## 许可证

该项目采用 MIT 许可证 - 详情请见 [LICENSE](LICENSE) 文件。

项目链接: [https://github.com/shifenhutu/django-admin-advanced-search](https://github.com/shifenhutu/django-admin-advanced-search)