from django import template
from pidman.usage_stats.models import fiscal_years

register = template.Library()

def show_usage_log_links(context):
    return {
        'years': fiscal_years()
    }

    
# Register the custom tag as an inclusion tag with takes_context=True.
register.inclusion_tag('access_logs.html', takes_context=True)(show_usage_log_links)