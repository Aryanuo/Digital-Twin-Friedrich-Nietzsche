import axios from "axios";

import { auth } from "../firebase";


const API_BASE =
    import.meta.env.VITE_API_URL ||
    "http://127.0.0.1:8000";


const api = axios.create({
    baseURL: API_BASE,
});


async function getAuthHeaders() {

    const user = auth.currentUser;

    // Guest user
    if (!user) {
        return {};
    }

    // Authenticated user
    const token =
        await user.getIdToken();

    return {
        Authorization:
            `Bearer ${token}`,
    };
}


export async function sendMessage(
    sessionId,
    message
) {

    const headers =
        await getAuthHeaders();


    const response = await api.post(
        "/chat",
        {
            session_id: sessionId,
            message,
        },
        {
            headers,
        }
    );


    return response.data;
}


export async function streamMessage(
    sessionId,
    message,
    {
        onToken,
        onSources,
    }
) {

    const headers = {
        "Content-Type":
            "application/json",
    };


    const user = auth.currentUser;


    // Add Firebase authentication
    // only for logged-in users.
    if (user) {

        const token =
            await user.getIdToken();

        headers.Authorization =
            `Bearer ${token}`;
    }


    const response = await fetch(
        `${API_BASE}/chat/stream`,
        {
            method: "POST",

            headers,

            body: JSON.stringify({
                session_id: sessionId,
                message,
            }),
        }
    );


    if (!response.ok) {

        throw new Error(
            `Request failed with status ${response.status}`
        );
    }


    if (!response.body) {

        throw new Error(
            "Streaming is not supported by this response."
        );
    }


    const reader =
        response.body.getReader();

    const decoder =
        new TextDecoder();

    let buffer = "";


    while (true) {

        const {
            value,
            done,
        } = await reader.read();


        if (done) {
            break;
        }


        buffer += decoder.decode(
            value,
            {
                stream: true,
            }
        );


        const events =
            buffer.split("\n\n");


        buffer =
            events.pop() || "";


        for (const event of events) {

            const dataLine =
                event
                    .split("\n")
                    .find((line) =>
                        line.startsWith("data:")
                    );


            if (!dataLine) {
                continue;
            }


            const jsonText =
                dataLine
                    .slice(5)
                    .trim();


            if (!jsonText) {
                continue;
            }


            const data =
                JSON.parse(jsonText);


            if (data.type === "token") {

                onToken?.(
                    data.text
                );

            }


            else if (
                data.type === "sources"
            ) {

                onSources?.(
                    data.sources || []
                );

            }


            else if (
                data.type === "error"
            ) {

                throw new Error(
                    data.message
                );

            }

        }
    }
}
export async function getConversations() {

    const headers =
        await getAuthHeaders();

    const response = await api.get(
        "/conversations",
        {
            headers,
        }
    );

    return response.data;
}


export async function getConversation(
    conversationId
) {

    const headers =
        await getAuthHeaders();

    const response = await api.get(
        `/conversations/${conversationId}`,
        {
            headers,
        }
    );

    return response.data;
}

export default api;