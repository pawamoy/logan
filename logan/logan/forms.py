from django import forms

from .models import Analysis


class AnalysisForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs["class"] = "form-control"
        self.fields["description"].widget.attrs["placeholder"] = "Enter description"
        self.fields["description"].widget.attrs["placeholder"] = "Enter description"

    def make_read_only(self):
        for field in self.fields.values():
            field.widget.attrs["readonly"] = True

    class Meta:
        model = Analysis
        fields = [
            "title",
            "description",
            "visibility",
        ]
