# Generated by Django 4.2.13 on 2024-05-22 11:39

from django.db import migrations, models
from olympia import amo
from olympia.constants.categories import CATEGORIES


def remove_accessibility_category(apps, schema_editor):
    Addon = apps.get_model('addons', 'Addon')
    AddonCategory = apps.get_model('addons', 'AddonCategory')
    other_category_id = CATEGORIES[amo.ADDON_EXTENSION]['other'].id
    old_accessibility_category_id = 74

    # Remove accessibilty category from every add-on.
    AddonCategory.objects.filter(category_id=old_accessibility_category_id).delete()

    # Find listed extensions left without a category.
    addon_ids_without_a_category = (
        Addon.unfiltered.filter(
            status=amo.STATUS_APPROVED,
            _current_version__isnull=False,
            type=amo.ADDON_EXTENSION,
        )
        .filter(
            ~models.Exists(AddonCategory.objects.filter(addon=models.OuterRef('pk')))
        )
        .values_list('pk', flat=True)
    )
    # Add "other" category to those.
    addon_categories_to_create = [
        AddonCategory(addon_id=addon_id, category_id=other_category_id)
        for addon_id in addon_ids_without_a_category
    ]
    AddonCategory.objects.bulk_create(addon_categories_to_create, ignore_conflicts=True)


class Migration(migrations.Migration):
    dependencies = [
        ('addons', '0050_remove_www_of_buymeacoffee'),
    ]

    operations = [
        migrations.RunPython(remove_accessibility_category, lambda a, s: None)
    ]
