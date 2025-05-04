import { useState } from 'react';
import { Button } from './components/ui/button'; // Adjust if needed
import { fetchWithAuth } from './lib/fetchWrapper'; // Ensure fetchWithAuth is imported

const Note = ({ id, title, content, relationship, createdAt, updatedAt }) => {
    const [editedTitle, setEditedTitle] = useState(title);
    const [editedContent, setEditedContent] = useState(content);
    const [createdAtState, setCreatedAtState] = useState(createdAt);
    const [updatedAtState, setUpdatedAtState] = useState(updatedAt);
    const [shareUsername, setShareUsername] = useState('');
    const [shareRole, setShareRole] = useState('observer');
    const [relationshipState, setRelationship] = useState(relationship);
    const canEdit = relationshipState === 'owner' || relationshipState === 'editor';
    const canDeleteOrShare = relationshipState === 'owner'; // Only owners can delete or share

    // Function to update user data in localStorage
    const updateLocalStorageUser = (updatedUserData) => {
        localStorage.setItem('user', JSON.stringify(updatedUserData));
    };

    const handleSave = async () => {
        try {
            console.log(`Saving note ${id}...`);

            // Prepare the data to send
            const updateData = {
                object_type: 'note',
                object_id: id,
            };

            // Only include title and content if they've changed
            if (editedTitle !== title) updateData.title = editedTitle;
            if (editedContent !== content) updateData.details = editedContent;

            // Make the request to the API to update the note
            const response = await fetchWithAuth('http://localhost:8000/update', {
                method: 'PATCH',
                body: JSON.stringify(updateData),
                headers: { 'Content-Type': 'application/json' },
            });

            if (response.ok) {
                console.log('Note updated successfully');

                // Update localStorage to reflect the new note data
                const userData = localStorage.getItem('user');
                if (userData) {
                    const parsedUser = JSON.parse(userData);

                    // Find the correct category (owner, editor, observer) based on the relationship
                    const updatedNotes = { ...parsedUser.notes };

                    // Update the specific note in the correct category (owner, editor, observer)
                    const category = parsedUser.notes[relationshipState]; // 'owner', 'editor', or 'observer'
                    updatedNotes[relationshipState] = category.map(note => {
                        if (note.id === id) {
                            return { ...note, title: editedTitle, details: editedContent, updated_at: new Date().toISOString() };
                        }
                        return note;
                    });

                    // Update the user object with the new notes
                    const updatedUser = { ...parsedUser, notes: updatedNotes };
                    updateLocalStorageUser(updatedUser); // Update the user in localStorage
                }

                // Refresh the note after saving
                handleRefresh(); // Trigger the refresh function to update the UI
                // window.location.reload(); // Or trigger a state update


            } else {
                console.error('Failed to update note');
            }
        } catch (error) {
            console.error('Save failed:', error);
        }
    };

    const handleRefresh = async () => {
        try {
            console.log(`Refreshing note ${id}...`);

            const response = await fetchWithAuth(`http://localhost:8000/view/note/${id}`, {
                method: 'GET',
            });

            if (!response.ok) {
                console.warn('Note no longer exists, removing from localStorage');

                const userData = JSON.parse(localStorage.getItem('user'));
                if (userData?.notes) {
                    const updatedNotes = { ...userData.notes };
                    Object.keys(updatedNotes).forEach(role => {
                        updatedNotes[role] = updatedNotes[role].filter(n => n.id !== id);
                    });

                    localStorage.setItem('user', JSON.stringify({
                        ...userData,
                        notes: updatedNotes,
                    }));
                }

                // Optionally, you could trigger a UI update or navigation if the note is gone
                window.location.reload()
                return
            }
            const note = await response.json()
            const oldRelationship = relationshipState; // Store the old relationship
            setRelationship(note.relationship); // Update relationshipState to new one

            // Optional: update localStorage
            const userData = JSON.parse(localStorage.getItem('user'));
            if (userData?.notes) {
                const updatedNotes = { ...userData.notes };

                // Remove from old relationship category
                if (updatedNotes[oldRelationship]) {
                    updatedNotes[oldRelationship] = updatedNotes[oldRelationship].filter(n => n.id !== note.id);
                }

                // Add or update in the new relationship category
                if (!updatedNotes[note.relationship]) {
                    updatedNotes[note.relationship] = [];
                }

                const index = updatedNotes[note.relationship].findIndex(n => n.id === note.id);
                if (index !== -1) {
                    updatedNotes[note.relationship][index] = note;
                } else {
                    updatedNotes[note.relationship].push(note);
                }

                localStorage.setItem('user', JSON.stringify({
                    ...userData,
                    notes: updatedNotes,
                }));
            }

            // Update local state with latest note data
            setEditedTitle(note.title);
            setEditedContent(note.details);
            setCreatedAtState(note.created_at);
            setUpdatedAtState(note.updated_at);

        } catch (error) {
            console.error('Refresh failed:', error);
        }
    };

    const handleUnshare = async () => {
        if (!shareUsername || !shareRole) {
            console.error('Username and role must be provided to unshare');
            return;
        }

        try {
            const url = `http://localhost:8000/remove/${shareRole}`;
            const response = await fetchWithAuth(url, {
                method: 'PUT',
                body: JSON.stringify({ username: shareUsername, note_id: id }),
                headers: { 'Content-Type': 'application/json' },
            });

            if (response.ok) {
                console.log(`Note unshared from ${shareUsername} as ${shareRole}`);
                setShareUsername('');
                setShareRole('observer');
            } else {
                console.error('Failed to unshare note');
            }
        } catch (error) {
            console.error('Unshare failed:', error);
        }
    };

    const handleDelete = async () => {
        try {
            console.log(`Deleting note ${id}...`);
            const response = await fetchWithAuth(`http://localhost:8000/delete/note/${id}`, {
                method: 'DELETE',
            });

            if (response.ok) {
                console.log('Note deleted successfully');

                // Remove the deleted note from localStorage
                const userData = localStorage.getItem('user');
                if (userData) {
                    const parsedUser = JSON.parse(userData);

                    // Remove the note from each category (owner, editor, observer) if it exists
                    const updatedNotes = { ...parsedUser.notes };

                    // Function to remove the note from a specific category
                    updatedNotes[relationshipState] = updatedNotes[relationshipState].filter(note => note.id !== id);


                    // Update the user object with the modified notes
                    const updatedUser = { ...parsedUser, notes: updatedNotes };
                    updateLocalStorageUser(updatedUser); // Update the user in localStorage
                }

                // Optionally, you can update the UI directly by reloading the page or updating the state
                window.location.reload(); // Or trigger a state update
            } else {
                console.error('Failed to delete note');
            }
        } catch (error) {
            console.error('Delete failed:', error);
        }
    };

    const handleShare = async () => {
        if (!shareUsername || !shareRole) {
            console.error('Username and role must be provided');
            return;
        }

        try {
            const url = `http://localhost:8000/add/${shareRole}`;
            const response = await fetchWithAuth(url, {
                method: 'PUT',
                body: JSON.stringify({ username: shareUsername, note_id: id }),
                headers: { 'Content-Type': 'application/json' },
            });

            if (response.ok) {
                console.log(`Note shared with ${shareUsername} as ${shareRole}`);
                setShareUsername('');
                setShareRole('observer');
            } else {
                console.error('Failed to share note');
            }
        } catch (error) {
            console.error('Share failed:', error);
        }
    };

    return (
        <div className="flex flex-col justify-start items-start h-auto p-4 bg-white shadow m-1 rounded-lg">
            {canEdit ? (
                <input
                    className="text-gray-800 font-semibold text-lg w-full border-b p-1 mb-2 focus:outline-none"
                    value={editedTitle}
                    onChange={(e) => setEditedTitle(e.target.value)}
                />
            ) : (
                <h4 className="font-semibold text-gray-800">{editedTitle}</h4>
            )}

            {canEdit ? (
                <textarea
                    className="text-neutral-800 mt-2 text-sm w-full border p-1 resize-none focus:outline-none"
                    value={editedContent}
                    onChange={(e) => setEditedContent(e.target.value)}
                    rows={6}
                />
            ) : (
                <p className="text-neutral-800 mt-4 text-[14px]">{editedContent}</p>
            )}

            <div className="flex gap-2 mt-4">
                {canEdit && (
                    <Button onClick={handleSave} variant="light">
                        Save
                    </Button>
                )}
                <Button onClick={handleRefresh} variant="light">
                    Refresh
                </Button>

                {canDeleteOrShare && (
                    <>
                        <Button onClick={handleDelete} variant="light" className="text-red-500">
                            Delete
                        </Button>
                    </>
                )}
            </div>

            {canDeleteOrShare && (
                <div className="mt-3 w-full">
                    <input
                        className="w-full border p-1 mb-2 text-sm"
                        placeholder="Username"
                        value={shareUsername}
                        onChange={(e) => setShareUsername(e.target.value)}
                    />
                    <select
                        className="w-full border p-1 mb-2 text-sm"
                        value={shareRole}
                        onChange={(e) => setShareRole(e.target.value)}
                    >
                        <option value="observer">Observer</option>
                        <option value="editor">Editor</option>
                    </select>
                    <div className="flex gap-2">
                        <Button onClick={handleShare} variant="light" className="text-blue-500">
                            Share
                        </Button>
                        <Button onClick={handleUnshare} variant="light" className="text-orange-500">
                            Unshare
                        </Button>
                    </div>
                </div>
            )}

            <p className="text-neutral-600 text-xs mt-2">Role: {relationshipState}</p>

            <div className="text-neutral-500 text-xs mt-2">
                <p>Created At: {new Date(createdAtState).toLocaleString()}</p>
                <p>Updated At: {new Date(updatedAtState).toLocaleString()}</p>
            </div>
        </div>
    )
};

export default Note;
