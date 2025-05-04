from models.note import UserRole
from models.user import User
from schemas.user import EditorSchema, ObserverSchema
from services.note_roles import modify_user_role_on_note


def add_editor_service(editor: EditorSchema, user: User):
    return modify_user_role_on_note(
        note_id=editor.note_id,
        username=editor.username,
        requester=user,
        target_role=UserRole.EDITOR,
        action="add"
    )


def add_observer_service(observer: ObserverSchema, user: User):
    return modify_user_role_on_note(
        note_id=observer.note_id,
        username=observer.username,
        requester=user,
        target_role=UserRole.OBSERVER,
        action="add"
    )
