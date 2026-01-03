from django.http import HttpResponseServerError, HttpResponse


class HealthCheckMiddleware:
    """
    HealthCheckMiddleware provides a readiness endpoint usable by Kubernetes for readiness probes.

    Taken from https://www.ianlewis.org/en/kubernetes-health-checks-django
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.method == "GET":
            if request.path == "/readiness":
                return self.readiness(request)

        return self.get_response(request)

    @staticmethod
    def readiness(request):
        # Connect to each database and do a generic standard SQL query
        # that doesn't write any data and doesn't depend on any tables
        # being present.
        try:
            from django.db import connections

            for name in connections:
                cursor = connections[name].cursor()
                cursor.execute("SELECT 1;")
                row = cursor.fetchone()
                if row is None:
                    return HttpResponseServerError("db: invalid response")
        except Exception:
            return HttpResponseServerError("db: cannot connect to database.")

        return HttpResponse("OK")
