import {
  DrawerContentComponentProps,
  DrawerContentScrollView,
  useDrawerStatus,
} from "@react-navigation/drawer";
import { useEffect, useRef, useState } from "react";
import {
  ActivityIndicator,
  Alert,
  Platform,
  Pressable,
  StyleSheet,
  Text,
  TextInput,
  View,
} from "react-native";

import {
  Conversation,
  deleteConversation,
  getConversations,
  renameConversation,
} from "../../../api/ai";
import { colors } from "../../../constants/colors";

const SEARCH_DEBOUNCE_MS = 300;

type ListStatus = "loading" | "ready" | "error";

interface Props extends DrawerContentComponentProps {
  activeConversationId: number | null;
  onSelectConversation: (id: number) => void;
  onNewChat: () => void;
}

// Fully self-contained: fetches, searches, renames and deletes its own
// data. Refreshes itself whenever the drawer opens (useDrawerStatus)
// rather than needing ChatScreen to push a "refresh" signal across --
// that would need lifted state or Context this feature doesn't otherwise
// need.
export function ConversationListDrawerContent({
  navigation,
  activeConversationId,
  onSelectConversation,
  onNewChat,
  ...rest
}: Props) {
  const [query, setQuery] = useState("");
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [status, setStatus] = useState<ListStatus>("loading");
  const [renamingId, setRenamingId] = useState<number | null>(null);
  const [renameValue, setRenameValue] = useState("");

  const debounceTimer = useRef<ReturnType<typeof setTimeout> | null>(null);
  // Guards against an earlier, slower request resolving after a later,
  // faster one -- only the most recently *started* request is allowed to
  // apply its result.
  const latestRequestId = useRef(0);

  function fetchList(q: string) {
    const requestId = ++latestRequestId.current;
    setStatus("loading");

    getConversations(q || undefined)
      .then(({ conversations: results }) => {
        if (requestId !== latestRequestId.current) return;
        setConversations(results);
        setStatus("ready");
      })
      .catch(() => {
        if (requestId !== latestRequestId.current) return;
        setStatus("error");
      });
  }

  const drawerStatus = useDrawerStatus();
  useEffect(() => {
    if (drawerStatus === "open") {
      fetchList(query);
    }
    // Only re-run when the drawer's own open/closed status changes --
    // not on every `query` change, which is handled by the debounced
    // handler below instead.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [drawerStatus]);

  function handleQueryChange(text: string) {
    setQuery(text);

    if (debounceTimer.current) {
      clearTimeout(debounceTimer.current);
    }

    debounceTimer.current = setTimeout(() => fetchList(text), SEARCH_DEBOUNCE_MS);
  }

  function handleSelect(conversation: Conversation) {
    onSelectConversation(conversation.id);
    navigation.closeDrawer();
  }

  function handleNewChat() {
    onNewChat();
    navigation.closeDrawer();
  }

  function startRename(conversation: Conversation) {
    setRenamingId(conversation.id);
    setRenameValue(conversation.title);
  }

  function commitRename(conversation: Conversation) {
    const title = renameValue.trim();
    setRenamingId(null);

    if (!title || title === conversation.title) {
      return;
    }

    renameConversation(conversation.id, title)
      .then(() => fetchList(query))
      .catch(() => fetchList(query));
  }

  // react-native-web's Alert.alert is a literal no-op stub (confirmed by
  // reading its source -- `static alert() {}`), so it never invokes any
  // button's onPress there. The web branch below mirrors what the web
  // app itself already does for this exact confirmation
  // (window.confirm), purely so this is testable outside a native
  // simulator; real iOS/Android always uses Alert.alert, unchanged.
  function confirmDelete(): Promise<boolean> {
    if (Platform.OS === "web") {
      return Promise.resolve(window.confirm("Delete this conversation? This can't be undone."));
    }

    return new Promise((resolve) => {
      Alert.alert("Delete this conversation?", "This can't be undone.", [
        { text: "Cancel", style: "cancel", onPress: () => resolve(false) },
        { text: "Delete", style: "destructive", onPress: () => resolve(true) },
      ]);
    });
  }

  async function handleDelete(conversation: Conversation) {
    const confirmed = await confirmDelete();

    if (!confirmed) {
      return;
    }

    deleteConversation(conversation.id)
      .then(() => {
        fetchList(query);
        if (conversation.id === activeConversationId) {
          onNewChat();
        }
      })
      .catch(() => fetchList(query));
  }

  return (
    <DrawerContentScrollView
      {...rest}
      contentContainerStyle={styles.container}
      keyboardShouldPersistTaps="handled"
    >
      <Pressable
        style={({ pressed }) => [styles.newChatButton, pressed && styles.newChatButtonPressed]}
        onPress={handleNewChat}
        android_ripple={{ color: colors.rippleOnLight }}
        accessibilityRole="button"
      >
        <Text style={styles.newChatButtonText}>+ New Chat</Text>
      </Pressable>

      <TextInput
        testID="conversation-search"
        style={styles.searchInput}
        placeholder="Search conversations..."
        placeholderTextColor={colors.textMuted}
        value={query}
        onChangeText={handleQueryChange}
      />

      {status === "loading" && conversations.length === 0 ? (
        <ActivityIndicator style={styles.stateIndicator} color={colors.primary} />
      ) : status === "error" ? (
        <Text style={styles.errorText}>Couldn't load conversations. Please try again.</Text>
      ) : conversations.length === 0 ? (
        <Text style={styles.emptyText}>
          {query ? `No conversations match "${query}".` : "No conversations yet."}
        </Text>
      ) : (
        conversations.map((conversation) => (
          <View
            key={conversation.id}
            testID="conversation-row"
            style={[styles.row, conversation.id === activeConversationId && styles.rowActive]}
          >
            {renamingId === conversation.id ? (
              <TextInput
                testID="conversation-rename-input"
                autoFocus
                style={styles.renameInput}
                value={renameValue}
                onChangeText={setRenameValue}
                onSubmitEditing={() => commitRename(conversation)}
                onBlur={() => commitRename(conversation)}
              />
            ) : (
              <Pressable
                style={({ pressed }) => [styles.rowMain, pressed && styles.rowMainPressed]}
                onPress={() => handleSelect(conversation)}
                android_ripple={{ color: colors.rippleOnLight }}
                accessibilityRole="button"
              >
                <Text style={styles.rowTitle} numberOfLines={1}>
                  {conversation.title}
                </Text>
              </Pressable>
            )}

            <View style={styles.rowActions}>
              <Pressable
                testID="conversation-rename-button"
                onPress={() => startRename(conversation)}
                style={({ pressed }) => [styles.actionButton, pressed && styles.actionButtonPressed]}
                android_ripple={{ color: colors.rippleOnLight }}
                hitSlop={8}
                accessibilityRole="button"
                accessibilityLabel={`Rename ${conversation.title}`}
              >
                <Text style={styles.actionText}>Rename</Text>
              </Pressable>
              <Pressable
                testID="conversation-delete-button"
                onPress={() => handleDelete(conversation)}
                style={({ pressed }) => [styles.actionButton, pressed && styles.actionButtonPressed]}
                android_ripple={{ color: colors.rippleOnLight }}
                hitSlop={8}
                accessibilityRole="button"
                accessibilityLabel={`Delete ${conversation.title}`}
              >
                <Text style={styles.actionTextDanger}>Delete</Text>
              </Pressable>
            </View>
          </View>
        ))
      )}
    </DrawerContentScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    padding: 12,
  },
  newChatButton: {
    borderWidth: 1,
    borderColor: colors.primary,
    borderRadius: 8,
    paddingVertical: 12,
    alignItems: "center",
    marginBottom: 12,
  },
  newChatButtonPressed: {
    opacity: 0.7,
  },
  newChatButtonText: {
    color: colors.primary,
    fontWeight: "700",
  },
  searchInput: {
    borderWidth: 1,
    borderColor: colors.border,
    borderRadius: 8,
    paddingHorizontal: 10,
    paddingVertical: 8,
    fontSize: 14,
    color: colors.text,
    marginBottom: 12,
  },
  stateIndicator: {
    marginTop: 24,
  },
  errorText: {
    color: colors.danger,
    backgroundColor: colors.dangerTint,
    padding: 10,
    borderRadius: 6,
    fontSize: 13,
    textAlign: "center",
  },
  emptyText: {
    color: colors.textMuted,
    fontSize: 13,
    textAlign: "center",
    marginTop: 24,
  },
  row: {
    paddingVertical: 10,
    borderBottomWidth: 1,
    borderBottomColor: colors.border,
  },
  rowActive: {
    backgroundColor: colors.brassTint,
  },
  rowMain: {
    marginBottom: 4,
    paddingVertical: 4,
  },
  rowMainPressed: {
    opacity: 0.7,
  },
  rowTitle: {
    fontSize: 14,
    fontWeight: "600",
    color: colors.text,
  },
  renameInput: {
    borderWidth: 1,
    borderColor: colors.brass,
    borderRadius: 6,
    paddingHorizontal: 6,
    paddingVertical: 4,
    fontSize: 14,
    color: colors.text,
    marginBottom: 4,
  },
  rowActions: {
    flexDirection: "row",
    gap: 12,
  },
  actionButton: {
    paddingVertical: 4,
  },
  actionButtonPressed: {
    opacity: 0.6,
  },
  actionText: {
    fontSize: 12,
    fontWeight: "600",
    color: colors.textMuted,
  },
  actionTextDanger: {
    fontSize: 12,
    fontWeight: "600",
    color: colors.danger,
  },
});
