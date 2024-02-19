import './App.css';
import { 
  MainContainer,
  Sidebar,
  Conversation,
  ConversationList,
  Avatar,
  Button,
} from '@chatscope/chat-ui-kit-react';
import {useState, useEffect} from 'react'
import {
  fetchConversations,
  startNewConversation
} from './conversationService.js'
import ConversationUI from './components/conversation.jsx';
import styles from '@chatscope/chat-ui-kit-styles/dist/default/styles.min.css';


function App() {
  const [currentConversationId, setCurrentConversationId] = useState("6012a554-78f4-4a61-93c2-b95c20d478e9");
  const [conversations, setConversations] = useState([]);

  const handleConversationChange = (conversationId) => {
    setCurrentConversationId(conversationId)
  }

  const newChat = async () => {
    const newConversationId = await startNewConversation();
    setCurrentConversationId(newConversationId);
    setConversations([...conversations, {last_message: "", id: newConversationId}]);
  }

  useEffect(() => {
    const getConversations = async () => {
      const conversations = await fetchConversations();
      setConversations(conversations);
    }

    getConversations();
  }, [currentConversationId])

  return (
    <div className="App">
      <div style={{
        height: "800px",
        position: "relative"
      }}>
            <MainContainer responsive>                
              <Sidebar position="left" scrollable={true}>
                <ConversationList>
                  {conversations.map((conversation, index) => (
                    conversation.id === currentConversationId ?
                      <Conversation key={index} name="ChatGPT" lastSenderName="ChatGPT" info={conversation.last_message} onClick={() => handleConversationChange(conversation.id)} active>
                        <Avatar src="robot-icon.png" name="GPT" status="available"/>
                      </Conversation>
                    :
                    <Conversation key={index} name="ChatGPT" lastSenderName="ChatGPT" info={conversation.last_message} onClick={() => handleConversationChange(conversation.id)}>
                      <Avatar src="robot-icon.png" name="GPT" status="available"/>
                    </Conversation>
                  ))}
                </ConversationList>
                <Button style={{color: "white", background: "#6ea9d7"}} border onClick={() => newChat()}>Start New Chat</Button>
              </Sidebar>
              
              <ConversationUI currentConversationId={currentConversationId} />
               
            </MainContainer>
          </div>
    </div>
  )
}

export default App;
