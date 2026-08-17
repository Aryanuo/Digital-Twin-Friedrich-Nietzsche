import { useEffect, useState } from "react";

import Header from "./components/Header";
import Sidebar from "./components/Sidebar";
import ChatWindow from "./components/ChatWindow";
import MessageInput from "./components/MessageInput";
import AuthPage from "./components/AuthPage";

import useChat from "./hooks/useChat";
import { useAuth } from "./context/AuthContext";

import "./styles/globals.css";


function App() {

    const {
        user,
        loading: authLoading
    } = useAuth();


    if (authLoading) {

        return (
            <div className="auth-loading">
                Loading...
            </div>
        );

    }


    return (
        <NietzscheApp
            user={user}
        />
    );
}


function NietzscheApp({ user }) {

    const [authOpen, setAuthOpen] =
        useState(false);


    const {
        conversations,
        activeConversationId,
        messages,
        loading,

        send,
        newConversation,
        selectConversation,
    } = useChat(user);


    const [sidebarOpen, setSidebarOpen] =
        useState(false);


    function handleNewConversation() {

        newConversation();

        setSidebarOpen(false);
    }

    useEffect(() => {

        if (user) {
            setAuthOpen(false);
        }

    }, [user]);
    return (
        <div className="app">

            <Header
                user={user}
                onLogin={() => setAuthOpen(true)}
            />


            <main className="main-content">

                {sidebarOpen && (
                    <div
                        className="sidebar-overlay"
                        onClick={() =>
                            setSidebarOpen(false)
                        }
                    />
                )}


                <div
                    className={
                        `sidebar-wrapper ${
                            sidebarOpen
                                ? "open"
                                : ""
                        }`
                    }
                >

                    <Sidebar
                        conversations={
                            conversations
                        }

                        activeConversationId={
                            activeConversationId
                        }

                        onNewConversation={
                            handleNewConversation
                        }

                        onSelectConversation={
                            selectConversation
                        }

                        onClose={() =>
                            setSidebarOpen(false)
                        }
                    />

                </div>


                <div className="chat-area">

                    <ChatWindow
                        messages={messages}
                        loading={loading}
                    />

                    <MessageInput
                        onSend={send}
                        loading={loading}
                    />

                </div>

            </main>
            {authOpen && (

                <div className="auth-modal-overlay">

                    <div className="auth-modal">

                        <button
                            className="auth-modal-close"
                            onClick={() =>
                                setAuthOpen(false)
                            }
                        >
                            ×
                        </button>

                        <AuthPage />

                    </div>

                </div>

            )}

        </div>
    );
}


export default App;