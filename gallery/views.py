from wagtail.admin.views.reports import PageReportView
from wagtail.core.models import Page


class UnpublishedChangesReportView(PageReportView):

    template_name = 'reports/unpublished_changes_report.html'
    
    def get_queryset(self):
        return Page.objects.filter(has_unpublished_changes=True)
