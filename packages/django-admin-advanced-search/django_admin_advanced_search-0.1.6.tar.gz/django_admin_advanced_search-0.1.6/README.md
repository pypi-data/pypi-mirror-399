# Django Admin Advanced Search

[![PyPI](https://img.shields.io/pypi/v/django-admin-advanced-search)](https://pypi.org/project/django-admin-advanced-search/)
[![License](https://img.shields.io/pypi/l/django-admin-advanced-search)](https://github.com/shifenhutu/django-admin-advanced-search/blob/main/LICENSE)
[![Python Version](https://img.shields.io/pypi/pyversions/django-admin-advanced-search)](https://pypi.org/project/django-admin-advanced-search/)

Advanced search syntax for Django Admin that enables powerful filtering capabilities for text fields directly from the search bar.

[中文版 说明](https://github.com/shifenhutu/django-admin-advanced-search/blob/main/README_zh.md)

## Features

- Enhanced search capabilities in Django Admin with advanced syntax for text fields
- Support for field-specific searches with various operators
- Case-sensitive and case-insensitive matching options
- Multiple conditions combination with AND logic
- Seamless integration with existing Django Admin interfaces
- Performance-conscious implementation with database-level filtering

## Requirements

- Python >= 3.12
- Django >= 5.1

Note: This package has been tested specifically on Django 5.1, 5.2 with Python 3.12. While it may work on other versions, compatibility is not guaranteed for versions outside this range.

This package is designed specifically for text field searches. For numeric and date/time field filtering, consider using [django-admin-rangefilter](https://github.com/silentsokolov/django-admin-rangefilter).

## Installation

```bash
pip install django-admin-advanced-search
```

## Usage

1. Add `django_admin_advanced_search` to your `INSTALLED_APPS`:

```python
INSTALLED_APPS = [
    ...
    'django_admin_advanced_search',
    ...
]
```

2. Use the advanced search in your admin classes:

```python
from django.contrib import admin
from django_admin_advanced_search.mixins import AdvancedSearchMixin

class MyModelAdmin(AdvancedSearchMixin, admin.ModelAdmin):
    search_fields = ['name', 'description', 'author__name']  # Fields that can be searched
    # Your other admin configuration

admin.site.register(MyModel, MyModelAdmin)
```

## Search Syntax

| Syntax | Description | Example | SQL Equivalent |
|--------|-------------|---------|----------------|
| `field:value` | Case-insensitive contains | `name:john` | `name ILIKE '%john%'` |
| `field:=value` | Case-insensitive exact | `name:=john` | `name ILIKE 'john'` |
| `field:==value` | Case-sensitive exact | `name:==John` | `name = 'John'` |
| `field:!value` | Case-sensitive contains | `name:!john` | `name LIKE '%john%'` |
| `field:*suffix` | Case-insensitive endswith | `name:*son` | `name ILIKE '%son'` |
| `field:!*suffix` | Case-sensitive endswith | `name:!*son` | `name LIKE '%son'` |
| `field:prefix*` | Case-insensitive startswith | `name:john*` | `name ILIKE 'john%'` |
| `field:!prefix*` | Case-sensitive startswith | `name:!john*` | `name LIKE 'john%'` |

## Combined Search

Advanced search syntax can be combined with plain text search. When both are present, the advanced search filters are applied first, then the plain text search is applied to the filtered results using Django's default search behavior.

Examples:
- `title:=Python lisa` - Find items with title exactly matching "Python" (case-insensitive) AND containing "lisa" in any search field
- `lisa title:=Python` - Same as above, order doesn't matter
- `title:django* tutorial` - Find items with titles starting with "django" (case-insensitive) AND containing "tutorial" in any search field

## Examples

- `title:django*` - Items with titles starting with "django" (case-insensitive)
- `author__name:*smith` - Items by authors whose names end with "smith" (case-insensitive)
- `title:==Learning Python` - Items with the exact title "Learning Python" (case-sensitive)
- `title:"Python Programming"` - Items with titles containing the exact phrase "Python Programming"
- `title:python author__name:john` - Items with titles containing "python" AND authors whose names contain "john"
- `title:=Python lisa` - Items with titles exactly matching "Python" (case-insensitive) AND containing "lisa" in any search field


## Testing

This package uses Django's built-in testing framework. To run the tests:

```bash
python -m django test tests --settings=tests.settings
```

## Database Collation and Performance Notes

- This package generates database-level filters, ensuring optimal performance
- For case-insensitive operations, the package uses the database's native case-insensitive comparison operators when available
- Make sure your database columns have appropriate collation settings for optimal performance
- Complex searches with multiple fields may generate complex SQL queries; consider adding database indexes on frequently searched fields
- When using related field lookups (e.g., `author__name:john`), ensure foreign key relationships are properly indexed

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

Project Link: [https://github.com/shifenhutu/django-admin-advanced-search](https://github.com/shifenhutu/django-admin-advanced-search)