from django.shortcuts import render
from http import HTTPStatus


def page_not_found(request, exception):
    # Переменная exception содержит отладочную информацию;
    # выводить её в шаблон пользовательской страницы 404 мы не станем
    return render(request, 'core/404.html', {'path': request.path}, status=404)


def csrf_failure(request, reason=''):
    return render(request, 'core/403csrf.html')


def permission_denied(request, exception):
    return render(request, 'core/403.html', status=HTTPStatus.FORBIDDEN)


def server_lost(request):
    return render(request, "misc/500.html", status=500)
