function Sidebar({
    conversations,
    activeConversationId,
    onNewConversation,
    onSelectConversation,
    onClose,
}) {

    return (
        <aside className="sidebar">

            <div className="sidebar-top">

                <div className="sidebar-heading">
                    <span>CONVERSATIONS</span>
                </div>

                <button
                    className="new-dialogue"
                    onClick={onNewConversation}
                >
                    <span className="new-dialogue-icon">
                        +
                    </span>

                    <span>
                        New Dialogue
                    </span>
                </button>

            </div>

            <div className="conversation-list">

                <div className="conversation-section">
                    TODAY
                </div>

                {conversations.map(
                    (conversation) => (

                        <button
                            key={conversation.id}
                            className={
                                `conversation-item ${
                                    conversation.id ===
                                    activeConversationId
                                        ? "active"
                                        : ""
                                }`
                            }
                            onClick={() => {
                                onSelectConversation(
                                    conversation.id
                                );

                                onClose?.();
                            }}
                        >

                            <span className="conversation-title">
                                {conversation.title}
                            </span>

                        </button>
                    )
                )}

            </div>

            <div className="sidebar-footer">

                <span>
                    Nietzsche Digital Twin
                </span>

            </div>

        </aside>
    );
}

export default Sidebar;