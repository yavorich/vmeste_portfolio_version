from django.views.generic import TemplateView


class SuccessPaymentView(TemplateView):
    template_name = "payment_result.html"
    extra_context = {"message": "Оплата прошла успешно"}


class FailPaymentView(TemplateView):
    template_name = "payment_result.html"
    extra_context = {"message": "Оплата не прошла"}
