from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """
    딕셔너리에서 키로 값을 가져오는 템플릿 필터
    사용법: {{ dictionary|get_item:key }}
    """
    return dictionary.get(key) 