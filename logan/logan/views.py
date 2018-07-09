#!/usr/bin/env python
from django.contrib.auth import get_user_model
from django.db.models import Q
from django.shortcuts import get_object_or_404, render, redirect

from .forms import AnalysisForm
from .models import Analysis


def home(request):
    return render(request, "logan/home.html", dict(
        my_analyses=Analysis.objects.filter(author=request.user),
        public_analyses=Analysis.objects.exclude(author=request.user).filter(
            visibility=Analysis.Visibility.PUBLIC)
    ))


def analysis(request, id):
    analysis_object = get_object_or_404(Analysis, id=id)

    if request.method == "POST":
        analysis_form = AnalysisForm(instance=analysis_object, data=request.POST)
        if analysis_form.is_valid():
            analysis_form.save()
        return redirect("analysis", id)

    analysis_form = AnalysisForm(instance=analysis_object)

    return render(request, "logan/analysis.html", dict(
        analysis=analysis_object,
        form=analysis_form
    ))


def user(request, id):
    user_object = get_object_or_404(get_user_model(), id=id)

    visibility_filter = Q(visibility=Analysis.Visibility.PUBLIC)
    if request.user.is_authenticated:
        visibility_filter |= Q(visibility=Analysis.Visibility.INTERNAL)

    user_analyses = Analysis.objects.filter(author=user_object).filter(visibility_filter)

    return render(request, "logan/user.html", dict(
        user=user_object,
        analyses=user_analyses
    ))
