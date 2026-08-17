import { useEffect, useRef } from "react";

import Message from "./Message";
import Loading from "./Loading";


function ChatWindow({
    messages,
    loading
}) {

    const bottomRef = useRef(null);

    const chatWindowRef = useRef(null);

    const shouldAutoScrollRef = useRef(true);


    function handleScroll() {

        const container =
            chatWindowRef.current;

        if (!container) {
            return;
        }


        const distanceFromBottom =
            container.scrollHeight -
            container.scrollTop -
            container.clientHeight;


        // Keep following the conversation only
        // when the user is already near the bottom.
        shouldAutoScrollRef.current =
            distanceFromBottom < 120;

    }


    useEffect(() => {

        if (
            shouldAutoScrollRef.current &&
            bottomRef.current
        ) {

            bottomRef.current.scrollIntoView({
                behavior: "auto",
                block: "end",
            });

        }

    }, [messages.length]);


    useEffect(() => {

        if (
            loading &&
            shouldAutoScrollRef.current &&
            bottomRef.current
        ) {

            bottomRef.current.scrollIntoView({
                behavior: "auto",
                block: "end",
            });

        }

    }, [loading]);


    if (messages.length === 0) {

        return (

            <div className="chat-window">

                <div className="empty-chat">

                    <div className="empty-symbol">
                        N
                    </div>

                    <h2>
                        What will you ask?
                    </h2>

                    <p>
                        Enter a question and begin
                        a conversation with
                        Friedrich Nietzsche.
                    </p>

                    <div className="suggestions">

                        <button>
                            What is nihilism?
                        </button>

                        <button>
                            What does suffering mean?
                        </button>

                        <button>
                            What is the will to power?
                        </button>

                    </div>

                </div>

            </div>

        );
    }


    return (

        <div
            className="chat-window"
            ref={chatWindowRef}
            onScroll={handleScroll}
        >

            <div className="messages-container">

                {messages.map(
                    (message, index) => (

                        <Message
                            key={index}
                            message={message}
                        />

                    )
                )}


                {loading && <Loading />}


                <div
                    ref={bottomRef}
                    className="chat-bottom"
                />

            </div>

        </div>

    );
}


export default ChatWindow;