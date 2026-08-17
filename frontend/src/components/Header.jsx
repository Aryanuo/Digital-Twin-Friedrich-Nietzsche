import { signOut } from "firebase/auth";

import { auth } from "../firebase";


function Header({ user, onLogin }) {


    async function handleLogout() {

        try {

            await signOut(auth);

        } catch (error) {

            console.error(
                "Logout error:",
                error
            );

        }
    }


    return (
        <header className="header">

            <div className="header-title">

                <h1>
                    Friedrich Nietzsche
                </h1>

                <p>
                    "Become who you are."
                </p>

            </div>


            <div className="auth-controls">

                {user ? (

                    <>

                        <span className="user-email">
                            {user.email}
                        </span>


                        <button
                            className="auth-header-button"
                            onClick={handleLogout}
                        >
                            Logout
                        </button>

                    </>

                ) : (

                    <button
                        className="auth-header-button"
                        onClick={onLogin}
                    >
                        Login
                    </button>

                )}

            </div>

        </header>
    );
}


export default Header;