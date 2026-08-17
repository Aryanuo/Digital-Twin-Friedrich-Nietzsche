import { useState } from "react";

import {
    signInWithEmailAndPassword,
} from "firebase/auth";

import { auth } from "../firebase";


function Login({ onSwitchToSignup }) {

    const [email, setEmail] = useState("");
    const [password, setPassword] = useState("");

    const [error, setError] = useState("");
    const [loading, setLoading] = useState(false);


    async function handleSubmit(e) {

        e.preventDefault();

        setError("");

        if (!email.trim() || !password) {
            setError(
                "Please enter your email and password."
            );
            return;
        }

        setLoading(true);

        try {

            await signInWithEmailAndPassword(
                auth,
                email.trim(),
                password
            );

        } catch (err) {

            console.error(
                "Login error:",
                err
            );

            switch (err.code) {

                case "auth/invalid-credential":
                    setError(
                        "Incorrect email or password."
                    );
                    break;

                case "auth/invalid-email":
                    setError(
                        "Please enter a valid email address."
                    );
                    break;

                case "auth/user-disabled":
                    setError(
                        "This account has been disabled."
                    );
                    break;

                default:
                    setError(
                        "Unable to sign in. Please try again."
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
                    Nietzsche Digital Twin
                </h1>

                <p className="auth-subtitle">
                    Continue your dialogue with
                    Friedrich Nietzsche.
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
                            placeholder="Your password"
                            autoComplete="current-password"
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
                            ? "Signing in..."
                            : "Sign In"}

                    </button>

                </form>


                <div className="auth-switch">

                    <span>
                        Don't have an account?
                    </span>

                    <button
                        type="button"
                        onClick={
                            onSwitchToSignup
                        }
                    >
                        Create account
                    </button>

                </div>

            </div>

        </div>
    );
}


export default Login;