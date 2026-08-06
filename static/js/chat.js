(function () {
    "use strict";

    var CHAT_ENDPOINT = "/ai/message";
    var NEW_CHAT_ENDPOINT = "/ai/new";
    var CONVERSATIONS_ENDPOINT = "/ai/conversations";

    // -----------------------------------------------------------------
    // Conversation state — the backend is the single source of truth
    // for conversation ids. This module only ever stores an id that the
    // server has already told it about: the initial page render (via
    // data-conversation-id) or a response's conversation_id field. It
    // never invents or guesses one.
    // -----------------------------------------------------------------
    var ConversationState = (function () {

        var conversationId = null;

        function init(initialId) {
            conversationId = initialId || null;
        }

        function get() {
            return conversationId;
        }

        function set(id) {
            conversationId = id;
        }

        return {
            init: init,
            get: get,
            set: set
        };
    })();

    // -----------------------------------------------------------------
    // Scrolling
    // -----------------------------------------------------------------
    var Scroller = (function () {

        function scrollToLatest() {

            var chatScroll = document.getElementById("chatScroll");

            if (!chatScroll) {
                return;
            }

            var messages = chatScroll.querySelectorAll(".message");
            var lastMessage = messages[messages.length - 1];

            if (lastMessage) {
                lastMessage.scrollIntoView({ block: "end" });
            } else {
                chatScroll.scrollTop = chatScroll.scrollHeight;
            }
        }

        return {
            scrollToLatest: scrollToLatest
        };
    })();

    // -----------------------------------------------------------------
    // Status region — the single shared aria-live channel for transient,
    // non-message announcements ("AI is typing…", copy confirmations).
    // Kept as one sr-only element rather than one aria-live region per
    // feature, so screen reader users get one predictable channel
    // instead of several competing ones. A token guards against a
    // stale auto-clear (e.g. from a copy confirmation) wiping out a
    // newer announcement (e.g. "AI is typing…") that was set after it.
    // -----------------------------------------------------------------
    var StatusRegion = (function () {

        var currentToken = 0;

        function el() {
            return document.getElementById("chatStatus");
        }

        function announce(text, autoClearMs) {

            var node = el();

            if (!node) {
                return;
            }

            currentToken += 1;
            var token = currentToken;

            node.textContent = text;

            if (autoClearMs) {
                setTimeout(function () {
                    if (token === currentToken) {
                        node.textContent = "";
                    }
                }, autoClearMs);
            }
        }

        function clear() {

            currentToken += 1;

            var node = el();

            if (node) {
                node.textContent = "";
            }
        }

        return {
            announce: announce,
            clear: clear
        };
    })();

    // -----------------------------------------------------------------
    // Message rendering — building/inserting DOM nodes into the log.
    // This module knows nothing about the conversation sidebar.
    // -----------------------------------------------------------------
    var MessageRenderer = (function () {

        var PLACEHOLDER_ITEMS = [
            "College prediction based on your rank",
            "Branch and college comparisons",
            "Recommendations by budget, branch or location",
            "JoSAA and CSAB counselling rules"
        ];

        function chatBox() {
            return document.getElementById("chatBox");
        }

        function escapeHtml(text) {
            var div = document.createElement("div");
            div.textContent = text;
            return div.innerHTML;
        }

        function clear() {
            chatBox().innerHTML = "";
        }

        function removePlaceholder() {

            var placeholder = chatBox().querySelector('[data-placeholder="true"]');

            if (placeholder) {
                placeholder.remove();
            }
        }

        function showPlaceholder() {

            var wrapper = document.createElement("div");
            wrapper.className = "message assistant";
            wrapper.setAttribute("data-placeholder", "true");

            var bubble = document.createElement("div");
            bubble.className = "bubble";
            bubble.appendChild(document.createTextNode("I'm your AI college counselor. I can help with:"));

            var list = document.createElement("ul");
            PLACEHOLDER_ITEMS.forEach(function (item) {
                var li = document.createElement("li");
                li.textContent = item;
                list.appendChild(li);
            });
            bubble.appendChild(list);
            bubble.appendChild(document.createTextNode("What would you like to know?"));

            wrapper.appendChild(bubble);
            chatBox().appendChild(wrapper);
        }

        function collapseLandingHeader() {

            var header = document.getElementById("chatPageHeader");

            if (header) {
                header.remove();
            }
        }

        function showLandingHeader() {

            if (document.getElementById("chatPageHeader")) {
                return;
            }

            var chatMain = document.querySelector(".chat-main");
            var chatScroll = document.getElementById("chatScroll");

            if (!chatMain || !chatScroll) {
                return;
            }

            var header = document.createElement("div");
            header.className = "page-header";
            header.id = "chatPageHeader";

            var eyebrow = document.createElement("p");
            eyebrow.className = "eyebrow";
            eyebrow.textContent = "AI Counselor";

            var heading = document.createElement("h1");
            heading.textContent = "Ask about colleges, cutoffs and counselling";

            var description = document.createElement("p");
            description.textContent =
                "Ask about eligibility, branch comparisons, recommendations, or JoSAA/CSAB counselling rules.";

            header.appendChild(eyebrow);
            header.appendChild(heading);
            header.appendChild(description);

            chatMain.insertBefore(header, chatScroll);
        }

        // Copies the rendered, visible text of the response (not the
        // original markdown source, which isn't available client-side).
        // Visible label feedback ("Copied!") is local to the button;
        // the screen-reader announcement goes through the shared
        // StatusRegion instead of a per-button live region.
        function buildMessageActions(bubble) {

            var actions = document.createElement("div");
            actions.className = "message-actions";

            var button = document.createElement("button");
            button.type = "button";
            button.className = "btn btn-ghost";
            button.textContent = "Copy";

            var resetTimer = null;

            function showButtonFeedback(label) {

                if (resetTimer) {
                    clearTimeout(resetTimer);
                }

                button.textContent = label;

                resetTimer = setTimeout(function () {
                    button.textContent = "Copy";
                    resetTimer = null;
                }, 1800);
            }

            button.addEventListener("click", function () {

                if (!navigator.clipboard || !navigator.clipboard.writeText) {
                    showButtonFeedback("Copy failed");
                    StatusRegion.announce("Copy failed.", 1800);
                    return;
                }

                navigator.clipboard.writeText(bubble.innerText).then(
                    function () {
                        showButtonFeedback("Copied!");
                        StatusRegion.announce("Response copied to clipboard.", 1800);
                    },
                    function () {
                        showButtonFeedback("Copy failed");
                        StatusRegion.announce("Copy failed.", 1800);
                    }
                );
            });

            actions.appendChild(button);

            return actions;
        }

        function appendMessage(role, contentHtml) {

            var wrapper = document.createElement("div");
            wrapper.className = "message " + role;

            var bubble = document.createElement("div");
            bubble.className = "bubble";
            bubble.innerHTML = contentHtml;

            wrapper.appendChild(bubble);

            if (role === "assistant") {
                wrapper.appendChild(buildMessageActions(bubble));
            }

            chatBox().appendChild(wrapper);

            return wrapper;
        }

        // Bulk history load (switching to a past conversation) — appends
        // every message with the log's aria-live off, then restores it.
        // Without this, reopening an old conversation would have a screen
        // reader read every past message aloud, which isn't a "new
        // response" and isn't useful.
        function appendHistory(messages) {

            var box = chatBox();
            var previousAriaLive = box.getAttribute("aria-live");

            box.setAttribute("aria-live", "off");

            messages.forEach(function (message) {
                appendMessage(message.role, message.content_html);
            });

            if (previousAriaLive !== null) {
                box.setAttribute("aria-live", previousAriaLive);
            }
        }

        function appendUserMessage(rawText) {
            return appendMessage("user", escapeHtml(rawText));
        }

        // Server-rendered history (initial page load, or a browser refresh
        // mid-conversation) is markup Jinja wrote directly -- it never goes
        // through appendMessage, so it wouldn't otherwise get a Copy button.
        // Runs once on init to bring it in line with everything added via JS.
        function hydrateExistingMessages() {

            var assistantBubbles = chatBox().querySelectorAll(
                '.message.assistant:not([data-placeholder]) .bubble:not(.error)'
            );

            assistantBubbles.forEach(function (bubble) {

                var wrapper = bubble.parentElement;

                if (wrapper.querySelector(".message-actions")) {
                    return;
                }

                wrapper.appendChild(buildMessageActions(bubble));
            });
        }

        function appendError(message) {

            var wrapper = document.createElement("div");
            wrapper.className = "message assistant";

            var bubble = document.createElement("div");
            bubble.className = "bubble error";
            bubble.textContent = message;

            wrapper.appendChild(bubble);
            chatBox().appendChild(wrapper);

            return wrapper;
        }

        return {
            clear: clear,
            removePlaceholder: removePlaceholder,
            showPlaceholder: showPlaceholder,
            collapseLandingHeader: collapseLandingHeader,
            showLandingHeader: showLandingHeader,
            appendMessage: appendMessage,
            appendHistory: appendHistory,
            appendUserMessage: appendUserMessage,
            appendError: appendError,
            hydrateExistingMessages: hydrateExistingMessages
        };
    })();

    // -----------------------------------------------------------------
    // Loading / typing indicator + input disabling
    // -----------------------------------------------------------------
    var LoadingIndicator = (function () {

        var typingBubble = null;

        function show() {

            var wrapper = document.createElement("div");
            wrapper.className = "message assistant";
            wrapper.id = "chatTypingIndicator";
            // The dots carry no text and the log only announces additions,
            // so without this the log would announce a blank message.
            // StatusRegion carries the actual "AI is typing…" announcement.
            wrapper.setAttribute("aria-hidden", "true");

            var bubble = document.createElement("div");
            bubble.className = "bubble typing-indicator";
            bubble.innerHTML =
                '<span class="typing-dot"></span>' +
                '<span class="typing-dot"></span>' +
                '<span class="typing-dot"></span>';

            wrapper.appendChild(bubble);
            document.getElementById("chatBox").appendChild(wrapper);

            typingBubble = wrapper;

            StatusRegion.announce("AI is typing…");

            Scroller.scrollToLatest();
        }

        function hide() {

            if (typingBubble) {
                typingBubble.remove();
                typingBubble = null;
            }

            StatusRegion.clear();
        }

        function setInputDisabled(disabled) {

            var textarea = document.getElementById("chatMessageInput");
            var button = document.getElementById("chatSendButton");

            if (textarea) {
                textarea.disabled = disabled;
            }

            if (button) {
                button.disabled = disabled;
            }
        }

        return {
            show: show,
            hide: hide,
            setInputDisabled: setInputDisabled
        };
    })();

    // -----------------------------------------------------------------
    // API communication
    // -----------------------------------------------------------------
    var ChatApi = (function () {

        var activeController = null;

        function sendMessage(message, conversationId) {

            if (activeController) {
                activeController.abort();
            }

            activeController = new AbortController();

            var payload = { message: message };

            if (conversationId) {
                payload.conversation_id = conversationId;
            }

            return fetch(CHAT_ENDPOINT, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(payload),
                signal: activeController.signal
            })
                .then(function (response) {

                    activeController = null;

                    return response.json().then(function (data) {
                        return {
                            ok: response.ok,
                            status: response.status,
                            data: data
                        };
                    });
                })
                .catch(function (err) {

                    activeController = null;

                    if (err.name === "AbortError") {
                        return { ok: false, aborted: true };
                    }

                    return { ok: false, networkError: true };
                });
        }

        function loadConversation(id) {
            return fetch(CONVERSATIONS_ENDPOINT + "/" + id, {
                headers: { Accept: "application/json" }
            }).then(function (response) {
                return response.json().then(function (data) {
                    return { ok: response.ok, data: data };
                });
            });
        }

        function startNew() {
            return fetch(NEW_CHAT_ENDPOINT, { method: "POST" });
        }

        return {
            sendMessage: sendMessage,
            loadConversation: loadConversation,
            startNew: startNew
        };
    })();

    // -----------------------------------------------------------------
    // Wiring — orchestrates the modules above, and the conversation
    // sidebar via its public interface only (ConversationSidebar.*).
    // -----------------------------------------------------------------
    function refreshSidebar() {
        if (window.ConversationSidebar) {
            window.ConversationSidebar.refresh();
        }
    }

    function handleSubmit(event) {

        event.preventDefault();

        var textarea = document.getElementById("chatMessageInput");
        var message = textarea.value.trim();

        if (!message) {
            return;
        }

        MessageRenderer.removePlaceholder();
        MessageRenderer.collapseLandingHeader();
        MessageRenderer.appendUserMessage(message);

        textarea.value = "";
        LoadingIndicator.setInputDisabled(true);
        LoadingIndicator.show();
        Scroller.scrollToLatest();

        ChatApi.sendMessage(message, ConversationState.get()).then(function (result) {

            LoadingIndicator.hide();
            LoadingIndicator.setInputDisabled(false);

            if (result.aborted) {
                return;
            }

            if (!result.ok) {

                var errorMessage =
                    (result.data && result.data.error && result.data.error.message) ||
                    "Something went wrong. Please try again.";

                MessageRenderer.appendError(errorMessage);
                Scroller.scrollToLatest();
                textarea.focus();
                return;
            }

            ConversationState.set(result.data.conversation_id);

            var assistantMessage = result.data.assistant_message;

            MessageRenderer.appendMessage(
                "assistant",
                assistantMessage.content_html
            );

            // assistant_message.blocks is always an array (never absent),
            // so this never needs a null-check — just a length check.
            if (assistantMessage.blocks.length > 0) {
                document.getElementById("chatBox").appendChild(
                    window.BlockRenderer.renderBlocks(assistantMessage.blocks)
                );
            }

            Scroller.scrollToLatest();
            textarea.focus();

            // Keeps the sidebar's ordering (by recent activity) and
            // auto-derived titles in sync after every exchange.
            refreshSidebar();
            if (window.ConversationSidebar) {
                window.ConversationSidebar.setActive(result.data.conversation_id);
            }
        });
    }

    function switchToConversation(id) {

        if (!id) {
            return;
        }

        LoadingIndicator.setInputDisabled(true);

        ChatApi.loadConversation(id).then(function (result) {

            LoadingIndicator.setInputDisabled(false);

            if (!result.ok) {
                return;
            }

            ConversationState.set(result.data.conversation.id);

            MessageRenderer.clear();
            MessageRenderer.collapseLandingHeader();
            MessageRenderer.appendHistory(result.data.messages);

            Scroller.scrollToLatest();

            var textarea = document.getElementById("chatMessageInput");
            if (textarea) {
                textarea.focus();
            }
        });
    }

    function startNewChat() {

        ChatApi.startNew();

        ConversationState.set(null);
        MessageRenderer.clear();
        MessageRenderer.showLandingHeader();
        MessageRenderer.showPlaceholder();

        var textarea = document.getElementById("chatMessageInput");
        if (textarea) {
            textarea.focus();
        }
    }

    function handleConversationDeleted() {
        // ConversationSidebar only invokes this when the deleted
        // conversation was the active one.
        startNewChat();
    }

    function init() {

        var chatScroll = document.getElementById("chatScroll");
        var form = document.getElementById("chatForm");

        ConversationState.init(
            chatScroll ? chatScroll.getAttribute("data-conversation-id") : null
        );

        MessageRenderer.hydrateExistingMessages();

        Scroller.scrollToLatest();
        window.addEventListener("load", Scroller.scrollToLatest);

        if (form) {
            form.addEventListener("submit", handleSubmit);
        }

        if (window.ConversationSidebar) {
            window.ConversationSidebar.init({
                initialConversationId: ConversationState.get(),
                onSelect: switchToConversation,
                onNewChat: startNewChat,
                onDelete: handleConversationDeleted
            });
        }
    }

    document.addEventListener("DOMContentLoaded", init);
})();
