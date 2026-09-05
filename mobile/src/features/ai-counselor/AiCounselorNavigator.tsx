import { createDrawerNavigator } from "@react-navigation/drawer";
import { useState } from "react";

import { headerScreenOptions } from "../../constants/navigationTheme";
import { AiCounselorDrawerParamList } from "../../navigation/types";
import { ConversationListDrawerContent } from "./components/ConversationListDrawerContent";
import { ChatScreen } from "./screens/ChatScreen";

const Drawer = createDrawerNavigator<AiCounselorDrawerParamList>();

// The one piece of state genuinely shared between the drawer's
// conversation list and the chat screen -- lifted no further than this
// component, which is their first common owner. Everything else
// (messages, search, the list itself) stays local to whichever of the
// two actually needs it. No Zustand, no Context: plain props down.
export function AiCounselorNavigator() {
  const [conversationId, setConversationId] = useState<number | null>(null);

  return (
    <Drawer.Navigator
      screenOptions={{ ...headerScreenOptions, title: "AI Counselor" }}
      drawerContent={(props) => (
        <ConversationListDrawerContent
          {...props}
          activeConversationId={conversationId}
          onSelectConversation={setConversationId}
          onNewChat={() => setConversationId(null)}
        />
      )}
    >
      <Drawer.Screen name="Chat">
        {() => <ChatScreen conversationId={conversationId} onConversationIdChange={setConversationId} />}
      </Drawer.Screen>
    </Drawer.Navigator>
  );
}
