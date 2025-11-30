from django.test import TestCase
from datetime import date, timedelta

from .scoring import calculate_scores


class ScoringTests(TestCase):

    def test_overdue_tasks_get_higher_score(self):
        overdue_task = {
            "title": "Overdue",
            "due_date": (date.today() - timedelta(days=2)).isoformat(),
            "estimated_hours": 2,
            "importance": 5,
            "dependencies": [],
        }
        future_task = {
            "title": "Future",
            "due_date": (date.today() + timedelta(days=10)).isoformat(),
            "estimated_hours": 2,
            "importance": 5,
            "dependencies": [],
        }

        results = calculate_scores([overdue_task, future_task])
        self.assertGreater(results[0]['score'], results[1]['score'])
        self.assertEqual(results[0]['title'], "Overdue")

    def test_missing_importance_uses_default(self):
        task = {
            "title": "No importance",
            "due_date": None,
            "estimated_hours": 1,
            "dependencies": [],
        }
        result = calculate_scores([task])[0]
        # default importance is 5, score should reflect that
        self.assertEqual(result['importance'], 5)

    def test_circular_dependency_flagged(self):
        tasks = [
            {
                "id": 1,
                "title": "Task A",
                "due_date": None,
                "estimated_hours": 1,
                "importance": 5,
                "dependencies": [2],
            },
            {
                "id": 2,
                "title": "Task B",
                "due_date": None,
                "estimated_hours": 1,
                "importance": 5,
                "dependencies": [1],
            },
        ]

        results = calculate_scores(tasks)
        circular_flags = [t['has_circular_dependency'] for t in results]
        self.assertTrue(all(circular_flags))