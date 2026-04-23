from django.contrib.auth.mixins import UserPassesTestMixin
from django.http import HttpResponseForbidden

ACCESS_DENIED_MESSAGE = "У вас нет доступа к этому действию."


class OwnerRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        obj = self.get_object()
        return obj.owner == self.request.user

    def handle_no_permission(self):
        return HttpResponseForbidden(ACCESS_DENIED_MESSAGE)
