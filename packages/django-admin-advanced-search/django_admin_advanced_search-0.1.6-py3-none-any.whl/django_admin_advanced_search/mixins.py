"""Advanced search functionality for Django Admin."""

from django.contrib import admin

from .parser import parse_advanced_search


class AdvancedSearchMixin(admin.ModelAdmin):
    """Mixin to add advanced search functionality to Django Admin.
    
    This mixin extends the default Django Admin search functionality
    with advanced syntax supporting field-specific searches.
    """

    def get_search_results(self, request, queryset, search_term):
        """
        Apply advanced search syntax to queryset.
        
        Supports the following syntax:
        - field:value → case-insensitive contains
        - field:=value → case-insensitive exact
        - field:==value → case-sensitive exact
        - field:!value → case-sensitive contains
        - field:*suffix → case-insensitive endswith
        - field:!*suffix → case-sensitive endswith
        - field:prefix* → case-insensitive startswith
        - field:!prefix* → case-sensitive startswith
        
        Only fields in search_fields are allowed for security.
        Falls back to default search if parsing fails.
        """
        search_term = search_term.strip()
        if not search_term:
            return super().get_search_results(request, queryset, search_term)

        try:
            parsed = self._parse_advanced_search(search_term)
        except Exception:
            # 解析失败 → 回退到默认行为
            return super().get_search_results(request, queryset, search_term)

        if parsed['has_advanced']:
            # 应用高级搜索过滤器
            qs = queryset
            for field, (lookup, value) in parsed['filters'].items():
                qs = qs.filter(**{f"{field}__{lookup}": value})
            
            # 如果还有普通文本，应用默认搜索逻辑
            if parsed['plain_text']:
                return super().get_search_results(request, qs, parsed['plain_text'])
            
            return qs.distinct(), False
        else:
            return super().get_search_results(request, queryset, parsed['plain_text'])
    
    def _parse_advanced_search(self, text):
        """Parse search terms using advanced syntax."""
        allowed_fields = getattr(self, 'search_fields', [])
        return parse_advanced_search(text, allowed_fields)