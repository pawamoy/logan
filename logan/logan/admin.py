from django.contrib import admin
from django.utils.safestring import mark_safe
from meerkat.logs.admin import RequestLogAdmin

from .models import Analysis


def build_analysis(modeladmin, request, queryset):
    analysis = Analysis.build(
        queryset, author=request.user, visibility=Analysis.Visibility.PRIVATE
    )
    modeladmin.message_user(
        request,
        mark_safe(
            'Analysis {pk} generated at <a href="{url}">{url}</a>'.format(
                pk=analysis.pk, url=analysis.url
            )
        ),
    )


build_analysis.short_description = "Generate analysis for the selected items"


RequestLogAdmin.actions.append(build_analysis)


class AnalysisAdmin(admin.ModelAdmin):
    list_display = ("pk", "author", "title", "description")


admin.site.register(Analysis, AnalysisAdmin)
