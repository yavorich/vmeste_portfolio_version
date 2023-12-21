from django.urls import reverse
from django.utils.html import format_html


class ManyToManyMixin:
    max_objects = 5

    @classmethod
    def links_to_objects(cls, objects):
        rel_list = "<ul>"
        for i, obj in enumerate(objects):
            if i == cls.max_objects:
                break
            model_name = obj.__class__.__name__.lower()
            link = reverse(f"admin:api_{model_name}_change", args=[obj.id])
            rel_list += "<li><a href='%s'>%s</a></li>" % (link, obj.__str__())
        rel_list += "</ul>"
        if objects.count() > cls.max_objects:
            rel_list += "<p>и другие</p>"
        return format_html(rel_list)
