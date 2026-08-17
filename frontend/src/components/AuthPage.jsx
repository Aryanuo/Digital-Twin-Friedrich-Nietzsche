import { useState } from "react";

import Login from "./Login";
import Signup from "./Signup";


function AuthPage() {

    const [showLogin, setShowLogin] =
        useState(true);


    if (showLogin) {

        return (
            <Login
                onSwitchToSignup={() =>
                    setShowLogin(false)
                }
            />
        );

    }


    return (
        <Signup
            onSwitchToLogin={() =>
                setShowLogin(true)
            }
        />
    );
}


export default AuthPage;