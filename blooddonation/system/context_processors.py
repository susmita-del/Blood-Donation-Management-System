import time


def session_countdown(request):

    if not request.user.is_authenticated:
        return {}

    # Admin: keep the normal session countdown and the inactivity
    # countdown separate. Normal session is the overall session lifetime;
    # inactivity countdown is only used when the Admin stops interacting.
    if request.user.is_staff:

        session_start = request.session.get("session_start")
        session_duration = request.session.get("session_duration")

        if session_start is not None and session_duration is not None:
            elapsed = time.time() - session_start
            session_remaining = max(0, int(session_duration - elapsed))
        else:
            session_remaining = 0

        last_activity = request.session.get("admin_last_activity")

        if last_activity:
            inactivity_remaining = max(
                0,
                int((30 * 60) - (time.time() - last_activity))
            )
        else:
            inactivity_remaining = 30 * 60

        return {
            "session_remaining": session_remaining,
            "inactivity_remaining": inactivity_remaining,
            "session_is_admin": True,
        }

    # Normal User: preserve the existing normal-session countdown.
    session_start = request.session.get("session_start")
    session_duration = request.session.get("session_duration")

    if session_start is None or session_duration is None:
        return {}

    elapsed = time.time() - session_start
    remaining = max(0, int(session_duration - elapsed))

    return {
        "session_remaining": remaining,
        "session_is_admin": False,
    }
