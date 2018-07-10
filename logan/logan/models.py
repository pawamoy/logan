import json
from datetime import datetime, timedelta
from collections import defaultdict

from django.conf import settings
from django.contrib.postgres.fields import JSONField
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.urls import reverse


class Analysis(models.Model):
    class Visibility:
        PUBLIC = "public"
        INTERNAL = "internal"
        PRIVATE = "private"
        CHOICES = (
            (PUBLIC, _("Public")),
            (INTERNAL, _("Internal")),
            (PRIVATE, _("Private")),
        )

    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    visibility = models.CharField(
        verbose_name=_("Visibility"), max_length=30, choices=Visibility.CHOICES,
        default=Visibility.PRIVATE
    )
    title = models.CharField(verbose_name=_("Title"), max_length=255)
    description = models.TextField(verbose_name=_("Description"), blank=True)
    created = models.DateTimeField(verbose_name=_("Created"), auto_now_add=True)
    modified = models.DateTimeField(verbose_name=_("Modified"), auto_now=True)
    data = JSONField(verbose_name=_("JSON data"))

    class Meta:
        verbose_name = _("Analysis")
        verbose_name_plural = _("Analyses")

    def __str__(self):
        return self.title

    @staticmethod
    def build(queryset, author, visibility=Visibility.PRIVATE):
        analysis = Analysis(
            author=author,
            visibility=visibility,
            title="%s: %s (%s items)" % (author, datetime.now(), queryset.count()),
        )

        references = dict()
        nodes = list()
        ip_dict = defaultdict(list)
        node_type = dict(
            GET="circle",
            POST="square",
            PUT="square",
            PATCH="square",
            HEAD="triangle-up",
            OPTIONS="triangle-down",
            DELETE="cross",
            CONNECT="diamond",
            TRACE="diamond",
        )
        for ref, item in enumerate(queryset.order_by("datetime")):
            references[item] = ref
            node_dict = dict(
                size=max(20, min(200, item.bytes_sent / 500)),
                score=item.status_code,
                id=item.request,
                type=node_type.get(item.verb)
            )
            nodes.append(node_dict)
            ip_dict[item.client_ip_address].append(item)

        links = []
        delta = timedelta(seconds=6)
        for k in ip_dict.keys():
            for i, request_i in enumerate(ip_dict[k][:-1]):

                request_j = ip_dict[k][i + 1]
                if request_j.datetime - request_i.datetime <= delta:

                    links.append(
                        {
                            "source": references[request_i],
                            "target": references[ip_dict[k][i + 1]],
                        }
                    )
                # for j, request_j in enumerate(ip_dict[k][i+1:], i+1):
                #     try:
                #         if request_j.referrer.split('/', 3)[3] == request_i.url.lstrip('/'):
                #             links.append({'source': references[request_i],
                #                           'target': references[request_j]})
                #     except IndexError:
                #         pass

        data = {"directed": True, "multigraph": True, "links": links, "nodes": nodes}

        analysis.data = json.dumps(data)
        analysis.save()

        return analysis

    @property
    def url(self):
        return reverse("analysis", kwargs=dict(id=self.pk))
