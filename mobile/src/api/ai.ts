import { request } from "./client";

// The generic block envelope every response block shares, per the
// documented contract. `data` stays untyped here -- only the specific
// renderer for a given `type` knows its shape (features/ai-counselor/
// components/blocks/types.ts). Naming this on the wire type, not the
// client Message type, since content-carrying logic belongs to the
// rendering layer.
export interface ResponseBlock {
  type: string;
  version: number;
  data: unknown;
}

// The client-side chat message shape. blocks is optional: absent for
// user messages, and absent for messages loaded from history (blocks are
// transient, per the documented contract -- only present on a message
// fresh off a POST /chat response).
export interface Message {
  id: string;
  role: "user" | "assistant";
  content: string;
  blocks?: ResponseBlock[];
}

// Exported: also used for GET /conversations/<id>'s message list, which
// has this exact shape (never blocks -- see Message above).
export interface ChatMessageResponse {
  id: number;
  role: "user" | "assistant";
  content: string;
  created_at: string | null;
}

interface AssistantMessageResponse extends ChatMessageResponse {
  blocks: ResponseBlock[];
}

interface ChatResponse {
  conversation_id: number;
  answer: string;
  user_message: ChatMessageResponse;
  assistant_message: AssistantMessageResponse;
  meta: { elapsed_ms: number };
}

// conversationId is omitted from the request body entirely (not sent as
// null) to start a new conversation, per the documented contract.
export function sendMessage(message: string, conversationId: number | null): Promise<ChatResponse> {
  const body: { message: string; conversation_id?: number } = { message };

  if (conversationId !== null) {
    body.conversation_id = conversationId;
  }

  return request<ChatResponse>("/ai/chat", {
    method: "POST",
    body: JSON.stringify(body),
  });
}

export interface Conversation {
  id: number;
  title: string;
  title_is_custom: boolean;
  created_at: string | null;
  updated_at: string | null;
}

interface ConversationDetail extends Conversation {
  messages: ChatMessageResponse[];
}

// Omitting q entirely (not sending an empty string) when there's no
// search term -- matches how conversationId is omitted above, and the
// documented contract treats an absent/empty q identically anyway.
export function getConversations(q?: string): Promise<{ conversations: Conversation[] }> {
  const suffix = q ? `?q=${encodeURIComponent(q)}` : "";
  return request(`/ai/conversations${suffix}`);
}

export function getConversation(id: number): Promise<{ conversation: ConversationDetail }> {
  return request(`/ai/conversations/${id}`);
}

export function renameConversation(id: number, title: string): Promise<{ conversation: Conversation }> {
  return request(`/ai/conversations/${id}`, {
    method: "PATCH",
    body: JSON.stringify({ title }),
  });
}

export function deleteConversation(id: number): Promise<void> {
  return request(`/ai/conversations/${id}`, { method: "DELETE" });
}
