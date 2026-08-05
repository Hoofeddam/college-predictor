from memory.conversation_memory import (
    load,
    save,
    clear
)

save(
    1,
    {
        "intent": "recommendation",
        "data": {
            "exam": "JEE Advanced"
        }
    }
)

print(load(1))

clear(1)

print(load(1))