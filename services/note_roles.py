from fastapi import HTTPException

from models import storage
from models.note import NoteUserLink, UserRole
from models.user import User


def modify_user_role_on_note(note_id: str, username: str, requester: User, target_role: UserRole, action: str):
    # Verify requester is the OWNER
    owner_link = storage.get("link", user_id=requester.id, note_id=note_id)
    if not (owner_link and owner_link.role == UserRole.OWNER):
        raise HTTPException(
            status_code=403,
            detail="Not authorized or note does not exist"
        )

    # Find the user to modify
    target_user = storage.get("user", username=username)
    if not target_user or target_user == requester:
        raise HTTPException(
            status_code=400,
            detail="User does not exist or cannot modify self"
        )

    # Fetch existing link
    target_link = storage.get("link", user_id=target_user.id, note_id=note_id)

    if action == "add":
        if target_link:
            if target_link.role == target_role:
                raise HTTPException(
                    status_code=409,
                    detail=f"User is already a {target_role.name.lower()}"
                )
            target_link.role = target_role
        else:
            target_link = NoteUserLink(
                note_id=note_id,
                user_id=target_user.id,
                role=target_role
            )

        storage.new(target_link)
        storage.save()
        return {"detail": f"{target_role.name.capitalize()} role successfully added"}

    elif action == "remove":
        if not target_link or target_link.role != target_role:
            raise HTTPException(
                status_code=404,
                detail=f"{target_role.name.capitalize()} role not found"
            )

        storage.delete(target_link)
        storage.save()
        return {"detail": f"{target_role.name.capitalize()} role successfully removed"}

    else:
        raise ValueError("Invalid action: must be 'add' or 'remove'")
