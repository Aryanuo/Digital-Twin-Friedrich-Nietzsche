import { useRef, useState } from "react";

function MessageInput({ onSend, disabled = false }) {

    const [message, setMessage] = useState("");
    const textareaRef = useRef(null);

    function resizeTextarea() {

        const textarea = textareaRef.current;

        if (!textarea) return;

        textarea.style.height = "auto";

        const maxHeight = 140;

        textarea.style.height =
            `${Math.min(textarea.scrollHeight, maxHeight)}px`;
    }

    function handleChange(e) {

        setMessage(e.target.value);

        requestAnimationFrame(() => {
            resizeTextarea();
        });
    }

    function handleSubmit(e) {

        e.preventDefault();

        if (
            !message.trim() ||
            disabled
        ) {
            return;
        }

        onSend(message);

        setMessage("");

        requestAnimationFrame(() => {

            if (textareaRef.current) {
                textareaRef.current.style.height = "auto";
            }

        });
    }

    function handleKeyDown(e) {

        if (
            e.key === "Enter" &&
            !e.shiftKey
        ) {

            e.preventDefault();

            handleSubmit(e);
        }
    }

    return (

        <form
            className="message-input"
            onSubmit={handleSubmit}
        >

            <textarea
                ref={textareaRef}

                value={message}

                onChange={handleChange}

                onKeyDown={handleKeyDown}

                disabled={disabled}

                placeholder="Ask Nietzsche..."

                rows={1}

                spellCheck="true"

                aria-label="Message Nietzsche"
            />

            <button
                type="submit"
                disabled={
                    disabled ||
                    !message.trim()
                }
                aria-label="Send message"
            >
                ↑
            </button>

        </form>
    );
}

export default MessageInput;