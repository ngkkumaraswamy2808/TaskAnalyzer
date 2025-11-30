from datetime import date, datetime

DEFAULT_IMPORTANCE = 5
DEFAULT_ESTIMATED_HOURS = 1


def parse_due_date(value):
    """Accepts string (YYYY-MM-DD) or date, returns date or None."""
    if isinstance(value, date):
        return value
    if not value:
        return None
    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except (ValueError, TypeError):
        return None


def normalize_task(task_dict, generated_id):
    """
    Normalize raw task data:
    - ensure id
    - clean importance / estimated_hours / dependencies
    """
    task_id = task_dict.get('id') or generated_id

    title = task_dict.get('title') or f"Task {task_id}"

    importance = task_dict.get('importance', DEFAULT_IMPORTANCE)
    try:
        importance = int(importance)
    except (ValueError, TypeError):
        importance = DEFAULT_IMPORTANCE
    if importance < 1:
        importance = 1
    if importance > 10:
        importance = 10

    estimated_hours = task_dict.get('estimated_hours', DEFAULT_ESTIMATED_HOURS)
    try:
        estimated_hours = int(estimated_hours)
    except (ValueError, TypeError):
        estimated_hours = DEFAULT_ESTIMATED_HOURS
    if estimated_hours <= 0:
        estimated_hours = DEFAULT_ESTIMATED_HOURS

    due_date_raw = task_dict.get('due_date')
    due = parse_due_date(due_date_raw)

    deps = task_dict.get('dependencies') or []
    if not isinstance(deps, list):
        deps = []

    return {
        'id': task_id,
        'title': title,
        'due_date': due,
        'importance': importance,
        'estimated_hours': estimated_hours,
        'dependencies': deps,
        '_raw_due': due_date_raw,
    }


def detect_cycles(task_map):
    """
    Detect circular dependencies using DFS.
    task_map: {id: task_dict}
    Returns a set of ids that are in any cycle.
    """
    graph = {tid: task_map[tid]['dependencies'] for tid in task_map}
    visited = set()
    stack = set()
    cycle_nodes = set()

    def dfs(node):
        if node in stack:
            cycle_nodes.update(stack)
            return
        if node in visited:
            return
        visited.add(node)
        stack.add(node)
        for nbr in graph.get(node, []):
            if nbr in graph:  # ignore deps that are not known tasks
                dfs(nbr)
        stack.remove(node)

    for node in graph:
        if node not in visited:
            dfs(node)

    return cycle_nodes


def compute_dependents(task_map):
    """Count how many tasks depend on each task id."""
    dependents_count = {tid: 0 for tid in task_map}
    for tid, task in task_map.items():
        for dep in task['dependencies']:
            if dep in dependents_count:
                dependents_count[dep] += 1
    return dependents_count


def calculate_scores(tasks, strategy='smart_balance'):
    """
    Main function:
    - Normalize tasks
    - Detect cycles & dependents
    - Compute score per strategy
    - Return sorted list with explanation
    """
    # Normalize + assign ids
    normalized = []
    for index, t in enumerate(tasks):
        normalized.append(normalize_task(t, generated_id=index + 1))

    task_map = {t['id']: t for t in normalized}

    cycle_ids = detect_cycles(task_map)
    dependents_count = compute_dependents(task_map)

    today = date.today()
    scored_tasks = []

    for t in normalized:
        tid = t['id']
        due = t['due_date']
        days_until_due = None
        urgency_score = 0
        urgency_text = ""

        if due:
            days_until_due = (due - today).days
            if days_until_due < 0:
                urgency_score = 60
                urgency_text = f"Overdue by {-days_until_due} day(s)"
            elif days_until_due == 0:
                urgency_score = 50
                urgency_text = "Due today"
            elif days_until_due <= 3:
                urgency_score = 40
                urgency_text = f"Due soon (in {days_until_due} day(s))"
            elif days_until_due <= 7:
                urgency_score = 20
                urgency_text = f"Due this week (in {days_until_due} day(s))"
            else:
                urgency_score = 0
                urgency_text = f"Due later (in {days_until_due} day(s))"
        else:
            urgency_score = 0
            urgency_text = "No due date provided"

        importance_score = t['importance'] * 5
        importance_text = f"Importance {t['importance']}/10"

        effort_score = 0
        if t['estimated_hours'] <= 1:
            effort_score = 15
            effort_text = "Very quick task (≤1h)"
        elif t['estimated_hours'] <= 3:
            effort_score = 8
            effort_text = "Moderate effort (≤3h)"
        else:
            effort_score = 0
            effort_text = f"Long task (~{t['estimated_hours']}h)"

        deps_blocks = dependents_count.get(tid, 0)
        dependency_score = min(30, deps_blocks * 10)
        dep_parts = []
        if deps_blocks > 0:
            dep_parts.append(f"blocks {deps_blocks} other task(s)")
        if t['dependencies']:
            dep_parts.append(f"depends on {len(t['dependencies'])} task(s)")
        dependency_text = ", ".join(dep_parts) if dep_parts else "No dependencies involved"

        base_smart_score = urgency_score + importance_score + effort_score + dependency_score

        # Strategy-specific tweaking
        if strategy == 'fastest_wins':
            # Strongly reward low effort, lightly consider importance and urgency
            strategy_score = effort_score * 2 + importance_score * 0.5 + urgency_score * 0.5
            strategy_label = "Fastest Wins"
        elif strategy == 'high_impact':
            # Importance dominates, then blocking, then urgency
            strategy_score = importance_score * 2 + dependency_score + urgency_score * 0.5
            strategy_label = "High Impact"
        elif strategy == 'deadline_driven':
            # Urgency dominates
            strategy_score = urgency_score * 2 + importance_score + effort_score * 0.2
            strategy_label = "Deadline Driven"
        else:
            # Default: smart combination
            strategy_score = base_smart_score
            strategy_label = "Smart Balance"

        score = round(strategy_score, 2)

        # Priority label based on score
        if score >= 120:
            priority_label = "High"
        elif score >= 60:
            priority_label = "Medium"
        else:
            priority_label = "Low"

        explanation_parts = [
            urgency_text,
            importance_text,
            effort_text,
            dependency_text,
            f"Strategy: {strategy_label}",
        ]
        if tid in cycle_ids:
            explanation_parts.append("⚠ Part of a circular dependency chain")

        explanation = "; ".join(explanation_parts)

        scored_tasks.append({
            "id": tid,
            "title": t['title'],
            "due_date": t['due_date'].isoformat() if t['due_date'] else None,
            "estimated_hours": t['estimated_hours'],
            "importance": t['importance'],
            "dependencies": t['dependencies'],
            "score": score,
            "priority_label": priority_label,
            "explanation": explanation,
            "has_circular_dependency": tid in cycle_ids,
        })

    # Sort by score DESC
    scored_tasks.sort(key=lambda x: x['score'], reverse=True)
    return scored_tasks