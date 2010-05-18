from datetime import date

from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import ugettext_lazy as _

from feincms.models import Base

from plata.product import abstract


__all__ = ['Product', 'ProductPrice',
    'Category', 'Discount', 'TaxClass']


class TaxClass(abstract.TaxClass):
    class Meta:
        app_label = 'product'
        ordering = ['-priority']
        verbose_name = _('tax class')
        verbose_name_plural = _('tax classes')


class Category(abstract.Category):
    class Meta:
        app_label = 'product'
        ordering = ['ordering', 'name']
        verbose_name = _('category')
        verbose_name_plural = _('categories')


class Product(abstract.Product, Base):
    categories = models.ManyToManyField(Category,
        verbose_name=_('categories'), related_name='products',
        blank=True, null=True)

    class Meta:
        app_label = 'product'
        ordering = ['ordering', 'name']
        verbose_name = _('product')
        verbose_name_plural = _('products')

Product.register_regions(
    ('main', 'Main'),
    ('history', 'History'),
    )
from feincms.content.raw.models import RawContent
Product.create_content_type(RawContent)


class ProductPrice(abstract.ProductPrice):
    product = models.ForeignKey(Product, verbose_name=_('product'),
        related_name='prices')
    tax_class = models.ForeignKey(TaxClass, verbose_name=_('tax class'))

    class Meta:
        app_label = 'product'
        get_latest_by = 'id'
        ordering = ['-valid_from']
        verbose_name = _('product price')
        verbose_name_plural = _('product prices')


class Discount(abstract.DiscountBase):
    code = models.CharField(_('code'), max_length=30, unique=True)

    is_active = models.BooleanField(_('is active'), default=True)
    valid_from = models.DateField(_('valid from'), default=date.today)
    valid_until = models.DateField(_('valid until'), blank=True, null=True)

    class Meta:
        app_label = 'product'
        verbose_name = _('discount')
        verbose_name_plural = _('discounts')

    def validate(self, order):
        messages = []
        if not self.is_active:
            messages.append(_('Discount is inactive.'))

        today = date.today()
        if today < self.valid_from:
            messages.append(_('Discount is not active yet.'))
        if self.valid_until and today > self.valid_until:
            messages.append(_('Discount is expired.'))

        if messages:
            raise ValidationError(messages)

        return True