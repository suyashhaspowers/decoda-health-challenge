import { useState, useEffect } from "react";
import { 
    ChatContainer,
    MessageList,
    Message,
    MessageInput,
    Avatar,
    ConversationHeader,
    TypingIndicator
  } from '@chatscope/chat-ui-kit-react';
  import { fetchConversationHistory, sendMessage } from "../conversationService";

export default function ConversationUI(props) {
    const [messages, setMessages] = useState([]);
    const [messageInputValue, setMessageInputValue] = useState("");
    const [isGptTyping, setIsGptTyping] = useState(false);

    console.log(props.currentConversationId);
    console.log(messages);

    useEffect(() => {
        const getConversationHistory = async () => {
          let messages = await fetchConversationHistory(props.currentConversationId);

          // When a conversation does not have messages
          if (!Array.isArray(messages)) {
            messages = []
          }
          setMessages(messages);
        }
    
        getConversationHistory();
      }, [props.currentConversationId])

    const send = async () => {
        setIsGptTyping(true);
        setMessageInputValue("");
        const outgoingMessage = {
            message_text: messageInputValue,
            is_incoming: false
        }
        setMessages([...messages, outgoingMessage])

        const response = await sendMessage(messageInputValue, props.currentConversationId);

        const incomingMessage = {
            message_text: response,
            is_incoming: true
        }
        setMessages([...messages, outgoingMessage, incomingMessage]);
        setIsGptTyping(false);
    }

    return (
        <ChatContainer>
            <ConversationHeader>
                <ConversationHeader.Back />
                <Avatar src="robot-icon.png" name="ChatGPT" />
                <ConversationHeader.Content userName="ChatGPT" />     
            </ConversationHeader>
            <MessageList typingIndicator={isGptTyping ? <TypingIndicator content="ChatGPT is typing" /> : null}>
                {messages.map((message, index) => (
                    message.is_incoming ?
                        <Message model={{
                            message: message.message_text,
                            direction: "incoming",
                            position: "single"
                        }}>
                            <Avatar src='robot-icon.png' name="GPT" />
                        </Message>
                    :
                        <Message model={{
                            message: message.message_text,
                            direction: "outgoing",
                            position: "single"
                        }}>
                             <Avatar src='user-icon.png' name="GPT" />
                        </Message>
                ))}
            </MessageList>
            <MessageInput attachButton={false} placeholder="Type message here" value={messageInputValue} onChange={val => setMessageInputValue(val)} onSend={() => send()} />
        </ChatContainer>   
    );
}