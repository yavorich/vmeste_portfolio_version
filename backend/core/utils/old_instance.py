def get_old_instance(instance):
    if instance._state.adding or not instance.pk:
        return

    try:
        return instance.__class__.objects.get(pk=instance.pk)
    except instance.DoesNotExist:
        return
