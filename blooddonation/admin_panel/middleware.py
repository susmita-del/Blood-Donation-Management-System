import time

from django.contrib.auth import logout
from django.shortcuts import redirect
from django.contrib import messages


class AdminAutoLogoutMiddleware:

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):

        if request.user.is_authenticated and request.user.is_staff:

            last_activity = request.session.get("admin_last_activity")

            if last_activity:
                elapsed_time = time.time() - last_activity

                # 30 minutes of Admin inactivity
                if elapsed_time >= 30 * 60:
                    logout(request)
                    messages.warning(
                        request,
                        "Your session has expired due to 30 minutes of inactivity. Please login again."
                    )
                    return redirect("admin_panel:login")

            # Keep the server-side inactivity timestamp alive while the
            # Admin is making requests. Browser activity is also reported
            # by the Admin heartbeat endpoint.
            request.session["admin_last_activity"] = time.time()

        response = self.get_response(request)
        return response
