#!/usr/bin/env python
from django.contrib.auth import get_user_model
from django.core.exceptions import PermissionDenied
from django.db.models import Q
from django.shortcuts import get_object_or_404, render, redirect

from .forms import AnalysisForm
from .models import Analysis


def home(request):
    my_analyses = []
    visible_analyses = Analysis.objects.all()

    visibility_filter = Q(visibility=Analysis.Visibility.PUBLIC)
    if request.user.is_authenticated:
        visibility_filter |= Q(visibility=Analysis.Visibility.INTERNAL)
        my_analyses = Analysis.objects.filter(author=request.user)
        visible_analyses = visible_analyses.exclude(author=request.user)

    visible_analyses = visible_analyses.filter(visibility_filter)

    return render(request, "logan/home.html", dict(
        my_analyses=my_analyses,
        visible_analyses=visible_analyses
    ))


def analysis(request, id):
    analysis_object = get_object_or_404(Analysis, id=id)

    if analysis_object.author != request.user:
        if not (analysis_object.visibility == Analysis.Visibility.PUBLIC or (
            analysis_object.visibility == Analysis.Visibility.INTERNAL and
            request.user.is_authenticated
        )):
            raise PermissionDenied

    if request.method == "POST":
        if analysis_object.author != request.user:
            raise PermissionDenied
        analysis_form = AnalysisForm(instance=analysis_object, data=request.POST)
        if analysis_form.is_valid():
            analysis_form.save()
        return redirect("analysis", id)

    analysis_form = None
    if analysis_object.author == request.user:
        analysis_form = AnalysisForm(instance=analysis_object)

    return render(request, "logan/analysis.html", dict(
        analysis=analysis_object,
        form=analysis_form
    ))


def user(request, id):
    user_object = get_object_or_404(get_user_model(), id=id)

    user_analyses = Analysis.objects.filter(author=user_object)

    if user_object != request.user:

        visibility_filter = Q(visibility=Analysis.Visibility.PUBLIC)
        if request.user.is_authenticated:
            visibility_filter |= Q(visibility=Analysis.Visibility.INTERNAL)

        user_analyses = user_analyses.filter(visibility_filter)

    return render(request, "logan/user.html", dict(
        user=user_object,
        analyses=user_analyses
    ))
