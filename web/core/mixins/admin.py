from django.urls import reverse


class RedirectToChangeMixin:
    def redirect_to_change(self, obj_or_pk):
        pk = obj_or_pk.pk if hasattr(obj_or_pk, 'pk') else obj_or_pk
        opts = self.model._meta  # noqa
        current_app = self.admin_site.name  # noqa
        view_name = f"chat_admin:{opts.app_label}_{opts.model_name}_change"

        return reverse(view_name, args=(pk,), current_app=current_app)
