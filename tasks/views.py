import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from .scoring import calculate_scores


def _parse_tasks_from_body(request):
    """
    Helper to parse JSON body.
    Accepts either a list of tasks or {"tasks": [...]}
    """
    try:
        data = json.loads(request.body.decode('utf-8') or '[]')
    except json.JSONDecodeError:
        return None, "Invalid JSON body"

    if isinstance(data, list):
        return data, None
    if isinstance(data, dict) and 'tasks' in data and isinstance(data['tasks'], list):
        return data['tasks'], None

    return None, "Expected a JSON array or an object with 'tasks' key"


@csrf_exempt
def analyze_tasks(request):
    """
    POST /api/tasks/analyze/?strategy=smart_balance
    Body: list of tasks or {"tasks": [...]}

    Returns: {"tasks": [...], "strategy": "..."}
    """
    if request.method != "POST":
        return JsonResponse({"error": "Only POST allowed"}, status=405)

    tasks, error = _parse_tasks_from_body(request)
    if error:
        return JsonResponse({"error": error}, status=400)

    strategy = request.GET.get('strategy', 'smart_balance')
    scored = calculate_scores(tasks, strategy=strategy)

    return JsonResponse({
        "tasks": scored,
        "strategy": strategy,
    })


@csrf_exempt
def suggest_tasks(request):
    """
    POST /api/tasks/suggest/?strategy=smart_balance
    Body: same as analyze

    Returns top 3 tasks with explanations.
    """
    if request.method != "POST":
        return JsonResponse({"error": "Only POST allowed"}, status=405)

    tasks, error = _parse_tasks_from_body(request)
    if error:
        return JsonResponse({"error": error}, status=400)

    strategy = request.GET.get('strategy', 'smart_balance')
    scored = calculate_scores(tasks, strategy=strategy)

    top_three = scored[:3]

    return JsonResponse({
        "tasks": top_three,
        "strategy": strategy,
        "message": "Top 3 tasks suggested for today based on selected strategy.",
    })
    