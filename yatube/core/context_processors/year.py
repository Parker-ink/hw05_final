from datetime import date


def year(request):
    """Добавляет переменную с текущим годом."""
    current_year = date.today().year
    return {
        'year': current_year,
    }
