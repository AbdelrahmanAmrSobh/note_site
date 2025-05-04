import { useState, useEffect } from 'react';
import Note from './Note';
import { Button } from './components/ui/button';
import { useNavigate } from 'react-router-dom';
import { fetchWithAuth } from './lib/fetchWrapper'; // Assuming you have a fetch wrapper for requests

function App() {
    const [user, setUser] = useState(null); // User state
    const [notes, setNotes] = useState([]);
    const [loading, setLoading] = useState(true); // Loading state
    const navigate = useNavigate();

    // Fetch user data on component mount (after login)
    useEffect(() => {
        const fetchAndSyncUser = async () => {
            const localUserData = localStorage.getItem('user');

            if (!localUserData) {
                navigate('/login');
                return;
            }

            try {
                const parsedUser = JSON.parse(localUserData);
                const userId = parsedUser.id;

                const response = await fetchWithAuth(`http://localhost:8000/view/user/${userId}`, {
                    method: 'GET',
                });

                if (!response.ok) {
                    throw new Error('Failed to fetch user data');
                }

                const updatedUser = await response.json();

                // Update localStorage and state
                localStorage.setItem('user', JSON.stringify(updatedUser));
                setUser(updatedUser);
                setNotes(updatedUser.notes || []);
                setLoading(false);
            } catch (error) {
                console.error('Error syncing user:', error);
                navigate('/login'); // Optional fallback
            }
        };

        fetchAndSyncUser();
    }, [navigate]);

    const handleLogout = async () => {
        try {
            const response = await fetchWithAuth('http://localhost:8000/auth/logout', {
                method: 'GET',
            });
            if (response.ok) {
                // Clear user state, localStorage, and redirect to login page
                localStorage.removeItem('user');
                setUser(null);
                setNotes([])
                navigate('/login');
            } else {
                console.error('Logout failed');
            }
        } catch (error) {
            console.error('Logout error:', error);
        }
    };

    const handleCreateNote = async () => {
        try {
            // Create the new note
            const response = await fetchWithAuth('http://localhost:8000/create/note', {
                method: 'POST',
                body: JSON.stringify({ title: '', details: '' }),
                headers: { 'Content-Type': 'application/json' },
            });

            if (response.ok) {
                // Now fetch the updated user data and notes
                const userData = localStorage.getItem('user');
                if (userData) {
                    const parsedUser = JSON.parse(userData);

                    // Fetch updated user data to get new notes
                    const userResponse = await fetchWithAuth(`http://localhost:8000/view/user/${parsedUser.id}`, {
                        method: 'GET',
                    });

                    if (userResponse.ok) {
                        const updatedUserData = await userResponse.json();
                        localStorage.setItem('user', JSON.stringify(updatedUserData))
                        setUser(updatedUserData);
                        setNotes(updatedUserData.notes)
                        window.location.reload();
                    } else {
                        console.error('Failed to fetch updated user data');
                    }
                }
            } else {
                console.error('Failed to create note');
            }
        } catch (error) {
            console.error('Create note failed:', error);
        }
    };

    if (loading) {
        return <div>Loading...</div>; // Show loading message while fetching user data
    }

    return (
        <>
            <nav className='flex justify-between items-center m-1 h-[80px] bg-neutral-900 px-4 py-2 rounded-xl'>
                <h3 className='text-white font-semibold'>NOTES</h3>
                <div className='h-full flex justify-center items-center gap-4'>
                    <p className='text-white'>Welcome, {user?.username}</p>
                    <Button onClick={() => window.location.reload()} variant="light">
                        Refresh
                    </Button>
                    <Button onClick={handleLogout} variant="light">
                        Logout
                    </Button>
                </div>
            </nav>

            <div className='w-full h-[100vh] bg-neutral-100'>
                <div className='p-4'>
                    {/* Create Note Button */}
                    <Button onClick={handleCreateNote} variant="light" className="mb-4">
                        Create New Note
                    </Button>

                    {/* Display Notes */}
                    <div className='grid grid-cols-5 gap-2'>
                        {notes.length === 0 ? (
                            <p>No notes available.</p>
                        ) :
                            ['owner', 'editor', 'observer'].flatMap((role) =>
                                (notes[role] || []).map((note) => (
                                    <Note
                                        key={note.id}
                                        id={note.id}
                                        title={note.title}
                                        content={note.details}
                                        relationship={role}
                                        createdAt={note.created_at}
                                        updatedAt={note.updated_at}
                                    />
                                ))
                            )
                        }
                    </div>
                </div>
            </div>

        </>
    );
}

export default App;
