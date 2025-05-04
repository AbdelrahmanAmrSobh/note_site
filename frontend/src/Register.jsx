import { useState } from 'react';
import { Link, useNavigate } from "react-router-dom";
import { Button } from "./components/ui/button";
import { Input } from "./components/ui/input";
import { fetchWithAuth } from './lib/fetchWrapper'; // Assuming you have a fetch wrapper for requests

const Register = () => {
    const [username, setUsername] = useState('');
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState('');
    const [loading, setLoading] = useState(false);
    const navigate = useNavigate();

    const handleRegister = async (e) => {
        e.preventDefault();

        // Basic validation check (can be extended further)
        if (!username || !email || !password) {
            setError("All fields are required.");
            return;
        }

        setLoading(true);
        setError(''); // Clear previous errors

        try {
            const response = await fetchWithAuth('http://localhost:8000/create/user', {
                method: 'POST',
                body: JSON.stringify({ username, email, password }),
                headers: { 'Content-Type': 'application/json' },
            });

            if (response.ok) {
                // Successfully registered, redirect to login
                const successData = await response.json(); // Get response data if available
                console.log('Registration successful:', successData.message); // You can log success info if needed
                navigate('/login');
            } else {
                // Error response handling
                const errorData = await response.json();
                setError(errorData.detail || errorData.message || 'Registration failed');
            }
        } catch (error) {
            setError(error.message || 'Something went wrong. Please try again.');
        } finally {
            setLoading(false);
        }
    };


    return (
        <div className="flex justify-center items-center w-full h-[100vh] bg-neutral-100">
            <div className="flex flex-col items-center justify-center w-[500px] h-[500px] p-4 bg-white shadow rounded-xl">
                <h1 className="text-[35px] font-bold">NOTES</h1>
                <h4 className="text-[18px] font-semibold">Register</h4>

                {error && <p className="text-red-600">{error}</p>}

                <form onSubmit={handleRegister} className="w-full mt-4">
                    <Input
                        className={"w-[80%] mt-4"}
                        type="text"
                        placeholder="Username"
                        value={username}
                        onChange={(e) => setUsername(e.target.value)}
                    />
                    <Input
                        className={"w-[80%] mt-4"}
                        type="email"
                        placeholder="Email"
                        value={email}
                        onChange={(e) => setEmail(e.target.value)}
                    />
                    <Input
                        className={"w-[80%] mt-4"}
                        type="password"
                        placeholder="Password"
                        value={password}
                        onChange={(e) => setPassword(e.target.value)}
                    />
                    <Button className={"w-[80%] mt-4 cursor-pointer"} type="submit" disabled={loading}>
                        {loading ? 'Registering...' : 'Register'}
                    </Button>
                </form>

                <p className="text-[12px] my-4">
                    Already Have an Account?{' '}
                    <Link className="text-red-600" to="/login">
                        Login
                    </Link>
                </p>
            </div>
        </div>
    );
};

export default Register;
