import { useState } from "react";
import { Button } from "./components/ui/button";
import { Input } from "./components/ui/input";
import { useNavigate } from "react-router-dom";
import { fetchWithAuth } from './lib/fetchWrapper'; // Assuming you have a fetch wrapper for requests

const Login = () => {
    const [email, setEmail] = useState("");
    const [password, setPassword] = useState("");
    const [error, setError] = useState("");
    const [loading, setLoading] = useState(false);

    const navigate = useNavigate();

    const handleLogin = async (e) => {
        e.preventDefault();
        setLoading(true);
        setError(""); // Clear previous errors

        try {
            const response = await fetchWithAuth('http://localhost:8000/auth/login', {
                method: 'POST',
                body: JSON.stringify({ email, password }),
                headers: { 'Content-Type': 'application/json' },
            });

            if (response.ok) {
                // Successfully logged in, handle the response (e.g., store token)
                const data = await response.json();
                console.log("Login successful:", data);
                localStorage.setItem('user', JSON.stringify(data.user));  // Save user data in localStorage

                // Redirect to home page after successful login
                navigate("/");
            } else {
                // Handle error response
                const errorData = await response.json();
                setError(errorData.detail || 'Login failed');
            }
        } catch (error) {
            setError('Something went wrong. Please try again.');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="flex justify-center items-center w-full h-[100vh] bg-neutral-100">
            <div className="flex flex-col items-center justify-center w-[500px] h-[500px] p-4 bg-white shadow rounded-xl">
                <h1 className="text-[35px] font-bold">NOTES</h1>
                <h4 className="text-[18px] font-semibold">Login</h4>

                {error && <p className="text-red-600 text-sm">{error}</p>}

                <Input
                    className={"w-[80%] mt-4"}
                    type="text"
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
                <Button
                    className={"w-[80%] mt-4 cursor-pointer"}
                    onClick={handleLogin}
                    disabled={loading}
                >
                    {loading ? "Logging in..." : "Login"}
                </Button>
                <Button
                    className={"w-[80%] mt-2 cursor-pointer"}
                    variant="outline"
                    onClick={() => navigate("/register")}
                >
                    Register
                </Button>
            </div>
        </div>
    );
};

export default Login;
