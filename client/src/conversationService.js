export async function fetchConversations() {
    const response = await fetch("http://localhost:8000/conversations");
    const conversations = await response.json();
    return conversations.data;
}

export async function fetchConversationHistory(conversationId) {
    const response = await fetch(`http://localhost:8000/conversation/${conversationId}/messages`);
    const conversationHistory = await response.json();
    return conversationHistory.data;
}

export async function sendMessage(message, conversationId) {
    const newMessage = {
        conversation: conversationId,
        message_text: message,
        is_incoming: false
    }

    const response = await fetch(`http://localhost:8000/conversation/${conversationId}/message/send`, {
        method: "POST",
        headers: {
            'Content-Type': 'application/json'
          },
        body: JSON.stringify(newMessage)
    });
    const gptResponse = await response.json();
    return gptResponse.data;
}

export async function startNewConversation() {
    const response = await fetch(`http://localhost:8000/conversation/create`, {
        method: "POST",
        headers: {
            'Content-Type': 'application/json'
          },
    });
    const newConversation = await response.json();
    return newConversation.data;
}