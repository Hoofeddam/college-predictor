import { useEffect, useRef, useState } from "react";
import {
  ActivityIndicator,
  FlatList,
  KeyboardAvoidingView,
  ListRenderItemInfo,
  Platform,
  Pressable,
  StyleSheet,
  Text,
  TextInput,
  View,
} from "react-native";
import Markdown from "react-native-markdown-display";

import { ChatMessageResponse, Message, getConversation, sendMessage } from "../../../api/ai";
import { ApiError } from "../../../api/types";
import { colors } from "../../../constants/colors";
import { BlockList } from "../components/blocks/BlockList";

interface ChatScreenProps {
  conversationId: number | null;
  onConversationIdChange: (id: number) => void;
}

function toClientMessage(message: ChatMessageResponse): Message {
  return { id: String(message.id), role: message.role, content: message.content };
}

function MessageBubble({ message }: { message: Message }) {
  const isUser = message.role === "user";
  const blocks = !isUser ? message.blocks : undefined;

  return (
    <View>
      <View style={[styles.bubbleRow, isUser ? styles.bubbleRowUser : styles.bubbleRowAssistant]}>
        <View style={[styles.bubble, isUser ? styles.bubbleUser : styles.bubbleAssistant]}>
          {isUser ? (
            <Text style={styles.userText}>{message.content}</Text>
          ) : (
            <Markdown style={markdownStyles}>{message.content}</Markdown>
          )}
        </View>
      </View>
      {/* Rendered as a sibling below the bubble, not nested inside its
          80%-width constraint -- cards need the full row width, matching
          how the web app appends blocks alongside .message, not inside
          .bubble. */}
      {blocks && blocks.length > 0 ? <BlockList blocks={blocks} /> : null}
    </View>
  );
}

export function ChatScreen({ conversationId, onConversationIdChange }: ChatScreenProps) {
  const [messages, setMessages] = useState<Message[]>([]);
  const [loadingHistory, setLoadingHistory] = useState(false);
  const [input, setInput] = useState("");
  const [sending, setSending] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const listRef = useRef<FlatList<Message>>(null);

  // Not "is this conversation's data fresh" -- that would conflate
  // identity with sync state, and a POST succeeding doesn't mean the
  // server's canonical history has actually been fetched. This only
  // means "skip the very next automatic history fetch, because I just
  // handled this id-change myself via a live send." Anything that
  // explicitly wants a real GET later (pull-to-refresh, retry, a future
  // background sync) is free to call getConversation directly without
  // this guard being involved at all.
  const skipNextHistoryFetch = useRef(false);

  useEffect(() => {
    if (skipNextHistoryFetch.current) {
      skipNextHistoryFetch.current = false;
      return;
    }

    if (conversationId === null) {
      // ChatScreen owns clearing its own state when the id becomes null
      // (e.g. "New Chat" or the active conversation being deleted).
      setMessages([]);
      return;
    }

    let cancelled = false;
    setLoadingHistory(true);

    getConversation(conversationId)
      .then((data) => {
        if (cancelled) return;
        setMessages(data.conversation.messages.map(toClientMessage));
      })
      .catch(() => {
        if (cancelled) return;
        setError("Couldn't load this conversation. Please try again.");
      })
      .finally(() => {
        if (!cancelled) setLoadingHistory(false);
      });

    return () => {
      cancelled = true;
    };
  }, [conversationId]);

  const canSend = input.trim().length > 0 && !sending;

  async function handleSend() {
    const text = input.trim();

    if (!text || sending) {
      return;
    }

    setInput("");
    setError(null);
    setSending(true);

    const userMessage: Message = {
      id: `local-${Date.now()}`,
      role: "user",
      content: text,
    };
    setMessages((prev) => [...prev, userMessage]);

    try {
      const data = await sendMessage(text, conversationId);

      const assistantMessage: Message = {
        id: String(data.assistant_message.id),
        role: data.assistant_message.role,
        content: data.assistant_message.content,
        blocks: data.assistant_message.blocks,
      };
      setMessages((prev) => [...prev, assistantMessage]);

      if (data.conversation_id !== conversationId) {
        skipNextHistoryFetch.current = true;
        onConversationIdChange(data.conversation_id);
      }
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Something went wrong. Please try again.");
    } finally {
      setSending(false);
    }
  }

  function renderItem({ item }: ListRenderItemInfo<Message>) {
    return <MessageBubble message={item} />;
  }

  return (
    <KeyboardAvoidingView
      style={styles.container}
      behavior={Platform.OS === "ios" ? "padding" : Platform.OS === "android" ? "height" : undefined}
      keyboardVerticalOffset={Platform.OS === "ios" ? 90 : 0}
    >
      {loadingHistory ? (
        <View style={styles.emptyState}>
          <ActivityIndicator color={colors.primary} />
        </View>
      ) : messages.length === 0 ? (
        <View style={styles.emptyState}>
          <Text style={styles.emptyTitle}>Ask about colleges, cutoffs and counselling</Text>
          <Text style={styles.emptySubtitle}>
            Ask about eligibility, branch comparisons, recommendations, or JoSAA/CSAB counselling rules.
          </Text>
        </View>
      ) : (
        <FlatList
          testID="chat-message-list"
          ref={listRef}
          data={messages}
          keyExtractor={(item) => item.id}
          renderItem={renderItem}
          contentContainerStyle={styles.messageList}
          onContentSizeChange={() => listRef.current?.scrollToEnd({ animated: true })}
          keyboardShouldPersistTaps="handled"
        />
      )}

      {error ? <Text style={styles.error}>{error}</Text> : null}

      <View style={styles.inputRow}>
        <TextInput
          testID="chat-input"
          style={styles.input}
          placeholder="Ask me anything about engineering colleges..."
          placeholderTextColor={colors.textMuted}
          value={input}
          onChangeText={setInput}
          multiline
          editable={!sending}
        />
        <Pressable
          testID="chat-send"
          style={({ pressed }) => [styles.sendButton, !canSend && styles.sendButtonDisabled, pressed && styles.sendButtonPressed]}
          onPress={handleSend}
          disabled={!canSend}
          android_ripple={{ color: colors.rippleOnDark }}
          accessibilityRole="button"
        >
          {sending ? (
            <ActivityIndicator color={colors.surface} size="small" />
          ) : (
            <Text style={styles.sendButtonText}>Send</Text>
          )}
        </Pressable>
      </View>
    </KeyboardAvoidingView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: colors.background,
  },
  emptyState: {
    flex: 1,
    justifyContent: "center",
    padding: 24,
  },
  emptyTitle: {
    fontSize: 20,
    fontWeight: "700",
    color: colors.text,
    marginBottom: 8,
  },
  emptySubtitle: {
    fontSize: 15,
    color: colors.textMuted,
  },
  messageList: {
    padding: 16,
    gap: 12,
  },
  bubbleRow: {
    flexDirection: "row",
  },
  bubbleRowUser: {
    justifyContent: "flex-end",
  },
  bubbleRowAssistant: {
    justifyContent: "flex-start",
  },
  bubble: {
    maxWidth: "80%",
    borderRadius: 10,
    padding: 12,
  },
  bubbleUser: {
    backgroundColor: colors.primary,
  },
  bubbleAssistant: {
    backgroundColor: colors.surface,
    borderWidth: 1,
    borderColor: colors.border,
  },
  userText: {
    color: colors.surface,
    fontSize: 15,
  },
  error: {
    color: colors.danger,
    backgroundColor: colors.dangerTint,
    padding: 12,
    marginHorizontal: 16,
    borderRadius: 6,
    textAlign: "center",
  },
  inputRow: {
    flexDirection: "row",
    alignItems: "flex-end",
    padding: 12,
    gap: 8,
    borderTopWidth: 1,
    borderTopColor: colors.border,
    backgroundColor: colors.surface,
  },
  input: {
    flex: 1,
    borderWidth: 1,
    borderColor: colors.border,
    borderRadius: 8,
    padding: 10,
    maxHeight: 100,
    fontSize: 15,
    color: colors.text,
  },
  sendButton: {
    backgroundColor: colors.primary,
    borderRadius: 8,
    paddingHorizontal: 16,
    paddingVertical: 10,
    justifyContent: "center",
    alignItems: "center",
  },
  sendButtonDisabled: {
    opacity: 0.5,
  },
  sendButtonPressed: {
    opacity: 0.85,
  },
  sendButtonText: {
    color: colors.surface,
    fontWeight: "600",
  },
});

const markdownStyles = {
  body: { color: colors.text, fontSize: 15 },
  heading1: { color: colors.text, fontSize: 20, fontWeight: "700" as const },
  heading2: { color: colors.text, fontSize: 18, fontWeight: "700" as const },
  heading3: { color: colors.text, fontSize: 16, fontWeight: "700" as const },
  strong: { fontWeight: "700" as const },
  bullet_list_icon: { color: colors.text },
  ordered_list_icon: { color: colors.text },
};
