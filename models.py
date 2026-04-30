# Estruturas de dados e validação de tarefas.
from dataclasses import dataclass
from typing import Optional


@dataclass
class Task:
    # Representa uma tarefa cadastrada pelo usuário.
    id: int
    user_id: int
    title: str
    description: str
    priority: str
    due_date: Optional[str]
    status: str
    created_at: str

    @classmethod
    def from_row(cls, row):
        # Cria uma instância de Task a partir de uma linha retornada do banco.
        return cls(
            id=row["id"],
            user_id=row["user_id"],
            title=row["title"],
            description=row["description"],
            priority=row["priority"],
            due_date=row["due_date"],
            status=row["status"],
            created_at=row["created_at"],
        )

    def to_dict(self):
        # Converte o objeto Task em um dicionário para uso em templates.
        return {
            "id": self.id,
            "user_id": self.user_id,
            "title": self.title,
            "description": self.description,
            "priority": self.priority,
            "due_date": self.due_date,
            "status": self.status,
            "created_at": self.created_at,
        }


VALID_PRIORITIES = ("baixa", "media", "alta")
VALID_STATUSES = ("pendente", "concluida")


def validate_task_data(title: str, description: str, priority: str) -> bool:
    # Valida campos básicos da tarefa antes de salvar no banco.
    if not title or len(title.strip()) < 3:
        return False
    if not description or len(description.strip()) < 5:
        return False
    if priority not in VALID_PRIORITIES:
        return False
    return True


def validate_task_status(status: str) -> bool:
    # Garante que o status informado seja um valor válido.
    return status in VALID_STATUSES
