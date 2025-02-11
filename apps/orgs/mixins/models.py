# -*- coding: utf-8 -*-
#

from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.core.exceptions import ValidationError

from common.utils import get_logger
from ..utils import (
    set_current_org, get_current_org, current_org, filter_org_queryset
)
from ..models import Organization

logger = get_logger(__file__)

__all__ = [
    'OrgManager', 'OrgModelMixin', 'Organization'
]


class OrgManager(models.Manager):

    def all_group_by_org(self):
        from ..models import Organization
        orgs = list(Organization.objects.all())
        querysets = {}
        for org in orgs:
            org_id = org.id
            queryset = super(OrgManager, self).get_queryset().filter(org_id=org_id)
            querysets[org] = queryset
        return querysets

    def get_queryset(self):
        queryset = super(OrgManager, self).get_queryset()
        return filter_org_queryset(queryset)

    def set_current_org(self, org):
        if isinstance(org, str):
            org = Organization.get_instance(org)
        set_current_org(org)
        return self


    def bulk_create(self, objs, batch_size=None, ignore_conflicts=False):
        org = get_current_org()
        for obj in objs:
            if org.is_root():
                if not self.org_id:
                    raise ValidationError('Please save in a organization')
            else:
                obj.org_id = org.id
        return super().bulk_create(objs, batch_size, ignore_conflicts)


class OrgModelMixin(models.Model):
    org_id = models.CharField(
        max_length=36, blank=True, default='', verbose_name=_("Organization"), db_index=True
    )
    objects = OrgManager()

    sep = '@'

    def save(self, *args, **kwargs):
        org = get_current_org()
        # 这里不可以优化成, 因为 root 组织下可以设置组织 id 来保存
        # if org.is_root() and not self.org_id:
        #     raise ...
        if org.is_root():
            if not self.org_id:
                raise ValidationError('Please save in a organization')
        else:
            self.org_id = org.id
        return super().save(*args, **kwargs)

    @property
    def org(self):
        return Organization.get_instance(self.org_id)

    @property
    def org_name(self):
        return self.org.name

    @property
    def fullname(self, attr=None):
        name = ''
        if attr and hasattr(self, attr):
            name = getattr(self, attr)
        elif hasattr(self, 'name'):
            name = self.name
        elif hasattr(self, 'hostname'):
            name = self.hostname
        return name + self.sep + self.org_name

    def validate_unique(self, exclude=None):
        """
        Check unique constraints on the model and raise ValidationError if any
        failed.
        Form 提交时会使用这个检验
        """
        self.org_id = current_org.id
        if exclude and 'org_id' in exclude:
            exclude.remove('org_id')
        unique_checks, date_checks = self._get_unique_checks(exclude=exclude)

        errors = self._perform_unique_checks(unique_checks)
        date_errors = self._perform_date_checks(date_checks)

        for k, v in date_errors.items():
            errors.setdefault(k, []).extend(v)

        if errors:
            raise ValidationError(errors)

    class Meta:
        abstract = True
