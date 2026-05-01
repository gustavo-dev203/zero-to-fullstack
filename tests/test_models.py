import unittest

from models import Task, validate_task_data, validate_task_status


class ModelTests(unittest.TestCase):
    def test_task_from_row_and_to_dict(self):
        row = {
            "id": 1,
            "user_id": 2,
            "title": "Tarefa teste",
            "description": "Descrição detalhada da tarefa.",
            "priority": "alta",
            "due_date": "2026-05-01",
            "status": "pendente",
            "created_at": "2026-05-01T12:00:00+00:00",
        }
        task = Task.from_row(row)

        self.assertEqual(task.title, "Tarefa teste")
        self.assertEqual(task.to_dict()["due_date"], "2026-05-01")

    def test_validate_task_data(self):
        self.assertTrue(validate_task_data("Título válido", "Descrição longa o suficiente", "media"))
        self.assertFalse(validate_task_data("", "Descrição longa o suficiente", "media"))
        self.assertFalse(validate_task_data("Ti", "Descrição longa o suficiente", "media"))
        self.assertFalse(validate_task_data("Título válido", "x", "media"))
        self.assertFalse(validate_task_data("Título válido", "Descrição longa o suficiente", "urgente"))

    def test_validate_task_status(self):
        self.assertTrue(validate_task_status("pendente"))
        self.assertTrue(validate_task_status("concluida"))
        self.assertFalse(validate_task_status("cancelada"))
