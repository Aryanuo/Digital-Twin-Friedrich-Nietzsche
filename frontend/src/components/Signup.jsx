import { useState } from "react";

import {
    createUserWithEmailAndPassword,
} from "firebase/auth";

import { auth } from "../firebase";


function Signup({ onSwitchToLogin }) {

    const [email, setEmail] = useState("");
    const [password, setPassword] = useState("");
    const [confirmPassword, setConfirmPassword] =
        useState("");

    const [error, setError] = useState("");
    const [loading, setLoading] = useState(false);


    async function handleSubmit(e) {

        e.preventDefault();

        setError("");

        const cleanEmail = email.trim();

        if (!cleanEmail || !password || !confirmPassword) {

            setError(
                "Please fill in all fields."
            );

            return;
        }

        if (password.length < 6) {

            setError(
                "Password must be at least 6 characters."
            );

            return;
        }

        if (password !== confirmPassword) {

            setError(
                "Passwords do not match."
            );

            return;
        }

        setLoading(true);

        try {

            await createUserWithEmailAndPassword(
                auth,
                cleanEmail,
                password
            );

        } catch (err) {

            console.error(
                "Signup error:",
                err
            );

            switch (err.code) {

                case "auth/email-already-in-use":

                    setError(
                        "An account with this email already exists."
                    );

                    break;

                case "auth/invalid-email":

                    setError(
                        "Please enter a valid email address."
                    );

                    break;

                case "auth/weak-password":

                    setError(
                        "Password is too weak."
                    );

                    break;

                default:

                    setError(
                        "Unable to create your account. Please try again."
                    );
            }

        } finally {

            setLoading(false);

        }
    }


    return (
        <div className="auth-page">

            <div className="auth-card">

                <div className="auth-symbol">
                    N
                </div>

                <h1>
                    Create your account
                </h1>

                <p className="auth-subtitle">
                    Create an account to preserve
                    your conversations with Nietzsche.
                </p>


                <form
                    className="auth-form"
                    onSubmit={handleSubmit}
                >

                    <label>
                        Email

                        <input
                            type="email"
                            value={email}
                            onChange={(e) =>
                                setEmail(
                                    e.target.value
                                )
                            }
                            placeholder="you@example.com"
                            autoComplete="email"
                            disabled={loading}
                        />
                    </label>


                    <label>
                        Password

                        <input
                            type="password"
                            value={password}
                            onChange={(e) =>
                                setPassword(
                                    e.target.value
                                )
                            }
                            placeholder="At least 6 characters"
                            autoComplete="new-password"
                            disabled={loading}
                        />
                    </label>


                    <label>
                        Confirm password

                        <input
                            type="password"
                            value={confirmPassword}
                            onChange={(e) =>
                                setConfirmPassword(
                                    e.target.value
                                )
                            }
                            placeholder="Enter password again"
                            autoComplete="new-password"
                            disabled={loading}
                        />
                    </label>


                    {error && (
                        <div className="auth-error">
                            {error}
                        </div>
                    )}


                    <button
                        type="submit"
                        className="auth-submit"
                        disabled={loading}
                    >

                        {loading
                            ? "Creating account..."
                            : "Create Account"}

                    </button>

                </form>


                <div className="auth-switch">

                    <span>
                        Already have an account?
                    </span>

                    <button
                        type="button"
                        onClick={
                            onSwitchToLogin
                        }
                    >
                        Sign in
                    </button>

                </div>

            </div>

        </div>
    );
}


export default Signup;