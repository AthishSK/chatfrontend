"""Main chat area with messages and input."""

import reflex as rx
from ..state.chat_state import ChatState
from .message_bubble import message_bubble


def chat_header() -> rx.Component:
    """Chat header with room info."""
    return rx.hstack(
        # Mobile menu button
        rx.box(
            rx.button(
                rx.icon("menu", size=20),
                on_click=ChatState.toggle_sidebar,
                variant="ghost",
                size="2",
                class_name="lg:hidden",
            ),
            class_name="lg:hidden",
        ),
        rx.hstack(
            rx.avatar(
                fallback=rx.cond(
                    ChatState.current_room_name,
                    ChatState.current_room_name[:2].upper(),
                    "C",
                ),
                size="3",
                radius="full",
            ),
            rx.vstack(
                rx.text(
                    rx.cond(
                        ChatState.current_room_name,
                        ChatState.current_room_name,
                        "Chat Room",
                    ),
                    weight="500",
                    size="4",
                    class_name="truncate max-w-[200px]",
                ),
                rx.text(
                    "Online",
                    size="1",
                    class_name="text-green-600",
                ),
                spacing="0",
                align_items="start",
            ),
            spacing="3",
        ),
        rx.spacer(),
        # Actions
        rx.hstack(
            rx.button(
                rx.icon("search", size=18),
                variant="ghost",
                size="2",
            ),
            rx.button(
                rx.icon("more_vertical", size=18),
                variant="ghost",
                size="2",
            ),
            spacing="1",
        ),
        class_name="w-full items-center p-4 border-b border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800",
    )


def message_list() -> rx.Component:
    """Scrollable message list."""
    return rx.box(
        rx.cond(
            ChatState.messages.length() > 0,
            rx.vstack(
                rx.foreach(
                    ChatState.messages,
                    message_bubble,
                ),
                spacing="4",
                class_name="w-full p-4",
            ),
            # Empty state
            rx.center(
                rx.vstack(
                    rx.icon("message_square", size=64, class_name="text-gray-300"),
                    rx.text(
                        "No messages yet",
                        size="4",
                        weight="500",
                        class_name="text-gray-500",
                    ),
                    rx.text(
                        "Send a message to start the conversation",
                        size="2",
                        class_name="text-gray-400",
                    ),
                    spacing="3",
                    class_name="items-center",
                ),
                class_name="h-full",
            ),
        ),
        id="message-list",
        class_name="flex-1 overflow-y-auto bg-gray-50 dark:bg-gray-900",
    )


def typing_indicator() -> rx.Component:
    """Show typing indicator."""
    return rx.cond(
        ChatState.typing_users.length() > 0,
        rx.hstack(
            rx.text(
                f"{ChatState.typing_users[0]} is typing",
                size="1",
                class_name="text-gray-500 italic",
            ),
            rx.hstack(
                rx.box(class_name="w-1 h-1 bg-gray-500 rounded-full animate-bounce"),
                rx.box(class_name="w-1 h-1 bg-gray-500 rounded-full animate-bounce animation-delay-200"),
                rx.box(class_name="w-1 h-1 bg-gray-500 rounded-full animate-bounce animation-delay-400"),
                spacing="1",
            ),
            spacing="2",
            class_name="px-4 py-2",
        ),
    )


def message_input() -> rx.Component:
    """Message input area."""
    return rx.hstack(
        rx.button(
            rx.icon("paperclip", size=20),
            variant="ghost",
            size="3",
            class_name="cursor-pointer",
        ),
        rx.input(
            placeholder="Type a message...",
            value=ChatState.message_input,
            on_change=ChatState.set_message_input,
            on_key_down=lambda key: rx.cond(
                key == "Enter",
                ChatState.send_message,
            ),
            on_input=ChatState.send_typing_indicator,
            size="3",
            class_name="flex-1",
        ),
        rx.button(
            rx.icon("send", size=20),
            on_click=ChatState.send_message,
            size="3",
            color_scheme="red",
            disabled=ChatState.message_input == "",
            class_name="cursor-pointer",
        ),
        spacing="2",
        class_name="w-full p-4 border-t border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800",
    )


def chat_area() -> rx.Component:
    """Main chat area."""
    return rx.cond(
        ChatState.current_room_id,
        # Chat selected
        rx.vstack(
            chat_header(),
            message_list(),
            typing_indicator(),
            message_input(),
            spacing="0",
            class_name="flex-1 h-screen",
        ),
        # No chat selected
        rx.center(
            rx.vstack(
                rx.icon("messages", size=80, class_name="text-gray-300"),
                rx.heading(
                    "Select a chat",
                    size="6",
                    class_name="text-gray-500",
                ),
                rx.text(
                    "Choose a conversation from the sidebar to start messaging",
                    class_name="text-gray-400 text-center",
                ),
                spacing="4",
                class_name="items-center max-w-md",
            ),
            class_name="flex-1 h-screen bg-gray-50 dark:bg-gray-900",
        ),
    )