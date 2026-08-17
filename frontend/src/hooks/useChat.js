import {
    useEffect,
    useState,
} from "react";

import {
    sendMessage,
    streamMessage,
    getConversations,
    getConversation,
} from "../services/api";

function createConversation() {
    return {
        id: crypto.randomUUID(),
        title: "New Dialogue",
        messages: [],
    };
}

function createTitle(message) {
    const cleaned = message
        .replace(/\s+/g, " ")
        .trim();

    if (cleaned.length <= 32) {
        return cleaned;
    }

    return cleaned.slice(0, 32).trim() + "...";
}

export default function useChat(user) {

    const [conversations, setConversations] =
        useState(() => {

            if (user) {
                return [];
            }

            return [
                createConversation()
            ];
        });

    const [activeConversationId, setActiveConversationId] =
        useState(() => {

            if (user) {
                return null;
            }

            return conversations?.[0]?.id;
        });

            
    const [loading, setLoading] = useState(false);

    const [conversationLoading, setConversationLoading] =
    useState(false);

    useEffect(() => {

        let cancelled = false;

        async function loadConversations() {

            // ========================================
            // GUEST
            // ========================================

            if (!user) {

                const conversation =
                    createConversation();

                setConversations([
                    conversation
                ]);

                setActiveConversationId(
                    conversation.id
                );

                return;
            }

            // ========================================
            // AUTHENTICATED USER
            // ========================================

            setConversationLoading(true);

            try {

                const data =
                    await getConversations();

                if (cancelled) {
                    return;
                }

                // ------------------------------------
                // No saved conversations
                // ------------------------------------

                if (data.length === 0) {

                    const conversation =
                        createConversation();

                    setConversations([
                        conversation
                    ]);

                    setActiveConversationId(
                        conversation.id
                    );

                    return;
                }

                // ------------------------------------
                // Restore conversation list
                // ------------------------------------

                const restoredConversations =
                    data.map(
                        (conversation) => ({
                            id: conversation.id,
                            title: conversation.title,
                            messages: [],
                        })
                    );

                setConversations(
                    restoredConversations
                );

                setActiveConversationId(
                    restoredConversations[0].id
                );

            } catch (error) {

                console.error(
                    "Failed to load conversations:",
                    error
                );

                if (!cancelled) {

                    const conversation =
                        createConversation();

                    setConversations([
                        conversation
                    ]);

                    setActiveConversationId(
                        conversation.id
                    );
                }

            } finally {

                if (!cancelled) {
                    setConversationLoading(false);
                }

            }
        }

        loadConversations();

        return () => {
            cancelled = true;
        };

    }, [user]);

    const activeConversation = conversations.find(
        (conversation) =>
            conversation.id === activeConversationId
    );

    const messages = activeConversation?.messages || [];

    function updateConversation(
        conversationId,
        updater
    ) {
        setConversations((prev) =>
            prev.map((conversation) => {

                if (conversation.id !== conversationId) {
                    return conversation;
                }

                return updater(conversation);
            })
        );
    }

    function newConversation() {

        if (loading) {
            return;
        }

        const conversation = createConversation();

        setConversations((prev) => [
            conversation,
            ...prev,
        ]);

        setActiveConversationId(
            conversation.id
        );
    }

    async function selectConversation(id) {

    if (
        loading ||
        conversationLoading
    ) {
        return;
    }

    // ========================================
    // GUEST
    // ========================================

    if (!user) {

        setActiveConversationId(id);

        return;
    }

    // ========================================
    // AUTHENTICATED USER
    // ========================================

    setActiveConversationId(id);

        const existingConversation =
            conversations.find(
                (conversation) =>
                    conversation.id === id
            );

        // Already loaded
        if (
            existingConversation &&
            existingConversation.messages.length > 0
        ) {
            return;
        }

        try {

            setConversationLoading(true);

            const data =
                await getConversation(id);

            updateConversation(
                id,
                (conversation) => ({
                    ...conversation,

                    title: data.title,

                    messages:
                        data.messages.map(
                            (message) => ({
                                role: message.role,
                                content: message.content,

                                sources: [],

                                streaming: false,
                            })
                        ),
                })
            );

        } catch (error) {

            console.error(
                "Failed to load conversation:",
                error
            );

        } finally {

            setConversationLoading(false);
        }
    }

    async function send(message) {

        if (
            !message.trim() ||
            loading ||
            !activeConversationId
        ) {
            return;
        }

        const trimmedMessage =
            message.trim();

        const conversationId =
            activeConversationId;

        const userMessage = {
            role: "user",
            content: trimmedMessage,
        };

        updateConversation(
            conversationId,
            (conversation) => {

                const isFirstMessage =
                    conversation.messages.length === 0;

                return {
                    ...conversation,

                    title: isFirstMessage
                        ? createTitle(
                            trimmedMessage
                        )
                        : conversation.title,

                    messages: [
                        ...conversation.messages,
                        userMessage,
                    ],
                };
            }
        );

        setLoading(true);

        let started = false;

        try {

            await streamMessage(
                conversationId,
                trimmedMessage,

                {
                    onToken: (token) => {

                        if (!started) {

                            started = true;

                            setLoading(false);

                            updateConversation(
                                conversationId,
                                (conversation) => ({
                                    ...conversation,

                                    messages: [
                                        ...conversation.messages,

                                        {
                                            role: "assistant",
                                            content: token,
                                            sources: [],
                                            streaming: true,
                                        },
                                    ],
                                })
                            );

                            return;
                        }

                        updateConversation(
                            conversationId,
                            (conversation) => {

                                const messages =
                                    [...conversation.messages];

                                const lastIndex =
                                    messages.length - 1;

                                const lastMessage =
                                    messages[lastIndex];

                                if (
                                    lastMessage?.role !==
                                    "assistant"
                                ) {
                                    return conversation;
                                }

                                messages[lastIndex] = {
                                    ...lastMessage,

                                    content:
                                        lastMessage.content +
                                        token,
                                };

                                return {
                                    ...conversation,
                                    messages,
                                };
                            }
                        );
                    },

                    onSources: (sources) => {

                        updateConversation(
                            conversationId,
                            (conversation) => {

                                const messages =
                                    [...conversation.messages];

                                const lastIndex =
                                    messages.length - 1;

                                const lastMessage =
                                    messages[lastIndex];

                                if (
                                    lastMessage?.role !==
                                    "assistant"
                                ) {
                                    return conversation;
                                }

                                messages[lastIndex] = {
                                    ...lastMessage,
                                    sources,
                                    streaming: false,
                                };

                                return {
                                    ...conversation,
                                    messages,
                                };
                            }
                        );
                    },
                }
            );

        } catch (error) {

            console.error(
                "Streaming error:",
                error
            );

            if (!started) {

                updateConversation(
                    conversationId,
                    (conversation) => ({
                        ...conversation,

                        messages: [
                            ...conversation.messages,

                            {
                                role: "assistant",
                                content:
                                    "Nietzsche is temporarily unavailable. " +
                                    "Please try again shortly.",
                            },
                        ],
                    })
                );

            } else {

                updateConversation(
                    conversationId,
                    (conversation) => {

                        const messages =
                            [...conversation.messages];

                        const lastIndex =
                            messages.length - 1;

                        if (
                            messages[lastIndex]?.role ===
                            "assistant"
                        ) {

                            messages[lastIndex] = {
                                ...messages[lastIndex],
                                streaming: false,
                            };
                        }

                        return {
                            ...conversation,
                            messages,
                        };
                    }
                );
            }

        } finally {

            setLoading(false);

        }
    }

    return {
        conversations,
        activeConversationId,
        messages,
        loading,

        send,
        newConversation,
        selectConversation,
    };
}