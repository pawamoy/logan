#!/usr/bin/env python
from django.shortcuts import get_object_or_404, render

from .models import Analysis


def analysis(request, id):
    analysis_object = get_object_or_404(Analysis, id=id)
    return render(request, 'logan/analysis.html', dict(analysis=analysis_object))
