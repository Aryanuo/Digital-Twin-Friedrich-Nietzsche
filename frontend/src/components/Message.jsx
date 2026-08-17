import ReactMarkdown from "react-markdown";
import SourceCard from "./SourceCard";

function Message({ message }) {
    const isUser = message.role === "user";

    return (
        <div className={`message-row ${isUser ? "user-row" : "assistant-row"}`}>

            <div className="message-content">

                {!isUser && (
                    <div className="message-author">
                        FRIEDRICH NIETZSCHE
                    </div>
                )}

                {isUser && (
                    <div className="message-author user-author">
                        YOU
                    </div>
                )}

                <div className={`bubble ${isUser ? "user-bubble" : "assistant-bubble"}`}>

                    <div
                        className={
                            `markdown-content ${
                                message.streaming
                                    ? "streaming-content"
                                    : ""
                            }`
                        }
                    >

                        <ReactMarkdown>
                            {message.content}
                        </ReactMarkdown>

                    </div>

                </div>

                {!isUser &&
                    message.sources &&
                    message.sources.length > 0 && (

                        <SourceCard
                            sources={message.sources}
                        />

                    )
                }

            </div>

        </div>
    );
}

export default Message;