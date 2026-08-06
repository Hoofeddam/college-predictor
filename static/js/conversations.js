(function () {
    "use strict";

    // Deliberately self-contained: this module knows nothing about
    // markdown, blocks, or #chatBox. It only knows how to list, switch,
    // rename and delete conversations, and it talks to the rest of the
    // page purely through the callbacks passed into init(). It does not
    // share helper functions with chat.js/blocks.js on purpose.

    var LIST_ENDPOINT = "/ai/conversations";
    var SEARCH_DEBOUNCE_MS = 300;

    var callbacks = {
        onSelect: function () {},
        onNewChat: function () {},
        onDelete: function () {}
    };

    var activeConversationId = null;
    var currentQuery = "";
    var activeListController = null;
    var searchDebounceTimer = null;

    function el(tag, className, text) {
        var node = document.createElement(tag);

        if (className) {
            node.className = className;
        }

        if (text !== undefined && text !== null) {
            node.textContent = text;
        }

        return node;
    }

    function listContainer() {
        return document.getElementById("conversationList");
    }

    // Aborts any still-in-flight list request before starting a new one --
    // the same supersede-the-previous-request pattern chat.js already uses
    // for message sends -- so a slow, stale response (e.g. from an earlier
    // keystroke) can never overwrite a fresher one. Distinguishes three
    // outcomes for the caller: ok (with results, possibly empty), aborted
    // (a newer request has since taken over -- do nothing), or a genuine
    // failure (ok: false) so callers don't mistake "request failed" for
    // "no results".
    function fetchConversations(q) {

        if (activeListController) {
            activeListController.abort();
        }

        activeListController = new AbortController();

        var url = LIST_ENDPOINT;

        if (q) {
            url += "?q=" + encodeURIComponent(q);
        }

        return fetch(url, {
            headers: { Accept: "application/json" },
            signal: activeListController.signal
        })
            .then(function (response) {

                if (!response.ok) {
                    return { ok: false };
                }

                return response.json().then(function (data) {
                    return { ok: true, conversations: data.conversations || [] };
                });
            })
            .catch(function (err) {

                if (err.name === "AbortError") {
                    return { ok: false, aborted: true };
                }

                return { ok: false };
            });
    }

    function renameConversation(id, title) {
        return fetch(LIST_ENDPOINT + "/" + id, {
            method: "PATCH",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ title: title })
        }).then(function (response) {
            return response.json().then(function (data) {
                return { ok: response.ok, data: data };
            });
        });
    }

    function deleteConversationRequest(id) {
        return fetch(LIST_ENDPOINT + "/" + id, { method: "DELETE" });
    }

    function buildRow(conversation) {

        var row = el("div", "item-row conversation-row");
        row.dataset.conversationId = conversation.id;

        if (String(conversation.id) === String(activeConversationId)) {
            row.classList.add("is-active");
        }

        var main = el("div", "item-main conversation-row-main");

        var titleLink = el("a", null, conversation.title);
        titleLink.href = "#";
        titleLink.addEventListener("click", function (event) {
            event.preventDefault();
            selectConversation(conversation.id);
        });

        main.appendChild(titleLink);
        row.appendChild(main);

        var actions = el("div", "item-actions conversation-row-actions");

        var renameButton = el("button", null, "Rename");
        renameButton.type = "button";
        renameButton.addEventListener("click", function () {
            startRename(row, conversation);
        });

        var deleteButton = el("button", "danger", "Delete");
        deleteButton.type = "button";
        deleteButton.addEventListener("click", function () {
            handleDelete(conversation.id);
        });

        actions.appendChild(renameButton);
        actions.appendChild(deleteButton);
        row.appendChild(actions);

        return row;
    }

    function startRename(row, conversation) {

        var main = row.querySelector(".conversation-row-main");
        main.innerHTML = "";

        var input = document.createElement("input");
        input.type = "text";
        input.value = conversation.title;
        input.className = "conversation-rename-input";
        input.setAttribute("aria-label", "Rename conversation");

        main.appendChild(input);
        input.focus();
        input.select();

        var committed = false;

        function commit() {

            if (committed) {
                return;
            }

            committed = true;

            var newTitle = input.value.trim();

            if (!newTitle || newTitle === conversation.title) {
                refresh();
                return;
            }

            renameConversation(conversation.id, newTitle).then(function (result) {
                if (result.ok) {
                    conversation.title = result.data.conversation.title;
                }
                refresh();
            });
        }

        input.addEventListener("keydown", function (event) {
            if (event.key === "Enter") {
                event.preventDefault();
                commit();
            } else if (event.key === "Escape") {
                committed = true;
                refresh();
            }
        });

        input.addEventListener("blur", commit);
    }

    function handleDelete(id) {

        var confirmed = window.confirm("Delete this conversation? This can't be undone.");

        if (!confirmed) {
            return;
        }

        deleteConversationRequest(id).then(function (response) {

            if (!response.ok && response.status !== 404) {
                return;
            }

            var wasActive = String(id) === String(activeConversationId);

            refresh();

            if (wasActive) {
                callbacks.onDelete(id);
            }
        });
    }

    function selectConversation(id) {
        setActive(id);
        callbacks.onSelect(id);
        close();
    }

    function render(conversations) {

        var container = listContainer();

        if (!container) {
            return;
        }

        container.innerHTML = "";

        if (conversations.length === 0) {

            var message = currentQuery
                ? "No conversations match \"" + currentQuery + "\"."
                : "No conversations yet.";

            container.appendChild(el("div", "empty-state", message));
            return;
        }

        conversations.forEach(function (conversation) {
            container.appendChild(buildRow(conversation));
        });
    }

    function renderError() {

        var container = listContainer();

        if (!container) {
            return;
        }

        container.innerHTML = "";
        container.appendChild(el(
            "div",
            "empty-state error",
            "Couldn't load conversations. Please try again."
        ));
    }

    function refresh() {
        return fetchConversations(currentQuery).then(function (result) {

            if (result.aborted) {
                return;
            }

            if (!result.ok) {
                renderError();
                return;
            }

            render(result.conversations);
        });
    }

    function setActive(id) {

        activeConversationId = id;

        var rows = document.querySelectorAll(".conversation-row");

        rows.forEach(function (row) {
            var isActive = String(row.dataset.conversationId) === String(id);
            row.classList.toggle("is-active", isActive);
        });
    }

    // ---- mobile open/close (this module owns its own visibility state) ----

    function open() {
        var sidebar = document.getElementById("chatSidebar");
        var backdrop = document.getElementById("sidebarBackdrop");
        var toggle = document.getElementById("sidebarToggle");

        if (sidebar) sidebar.classList.add("is-open");
        if (backdrop) backdrop.classList.add("is-visible");
        if (toggle) toggle.setAttribute("aria-expanded", "true");
    }

    function close() {
        var sidebar = document.getElementById("chatSidebar");
        var backdrop = document.getElementById("sidebarBackdrop");
        var toggle = document.getElementById("sidebarToggle");

        if (sidebar) sidebar.classList.remove("is-open");
        if (backdrop) backdrop.classList.remove("is-visible");
        if (toggle) toggle.setAttribute("aria-expanded", "false");
    }

    function toggle() {
        var sidebar = document.getElementById("chatSidebar");

        if (sidebar && sidebar.classList.contains("is-open")) {
            close();
        } else {
            open();
        }
    }

    function init(options) {

        callbacks.onSelect = (options && options.onSelect) || callbacks.onSelect;
        callbacks.onNewChat = (options && options.onNewChat) || callbacks.onNewChat;
        callbacks.onDelete = (options && options.onDelete) || callbacks.onDelete;

        activeConversationId = (options && options.initialConversationId) || null;

        var newChatButton = document.getElementById("newChatButton");
        var toggleButton = document.getElementById("sidebarToggle");
        var backdrop = document.getElementById("sidebarBackdrop");
        var searchInput = document.getElementById("conversationSearch");

        if (newChatButton) {
            newChatButton.addEventListener("click", function () {
                setActive(null);
                callbacks.onNewChat();
                close();
            });
        }

        if (toggleButton) {
            toggleButton.addEventListener("click", toggle);
        }

        if (backdrop) {
            backdrop.addEventListener("click", close);
        }

        if (searchInput) {
            searchInput.addEventListener("input", function (event) {

                var value = event.target.value;

                if (searchDebounceTimer) {
                    clearTimeout(searchDebounceTimer);
                }

                searchDebounceTimer = setTimeout(function () {
                    currentQuery = value.trim();
                    refresh();
                }, SEARCH_DEBOUNCE_MS);
            });
        }

        refresh();
    }

    window.ConversationSidebar = {
        init: init,
        setActive: setActive,
        refresh: refresh
    };
})();
