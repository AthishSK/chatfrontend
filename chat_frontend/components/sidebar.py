"""Sidebar component with room list and user profile."""

import reflex as rx
from ..state.chat_state import ChatState


def room_item(room: dict) -> rx.Component:
    """Individual room list item."""
    return rx.box(
        rx.hstack(
            rx.avatar(
                fallback=room["name"][:2].upper(),
                size="3",
                radius="full",
                class_name="flex-shrink-0",
            ),
            rx.vstack(
                rx.hstack(
                    rx.text(
                        room["name"],
                        weight="500",
                        size="2",
                        class_name="truncate",
                    ),
                    rx.spacer(),
                    rx.cond(
                        room.get("unread_count", 0) > 0,
                        rx.badge(
                            str(room.get("unread_count", 0)),
                            color_scheme="red",
                            size="1",
                        ),
                    ),
                    class_name="w-full",
                ),
                rx.text(
                    room.get("last_message", "No messages yet"),
                    size="1",
                    class_name="text-gray-500 truncate w-full",
                ),
                spacing="1",
                class_name="flex-1 min-w-0",
            ),
            spacing="3",
            class_name="items-center w-full",
        ),
        on_click=lambda: ChatState.select_room(room["id"], room["name"]),
        class_name=rx.cond(
            ChatState.current_room_id == room["id"],
            "p-3 cursor-pointer rounded-lg bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800",
            "p-3 cursor-pointer rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors",
        ),
    )


def sidebar() -> rx.Component:
    """Render sidebar with rooms and user profile."""
    return rx.vstack(
        # User Profile Header
        rx.hstack(
            rx.avatar(
                src=rx.cond(
                    ChatState.current_user,
                    ChatState.current_user.get("avatar_url", ""),
                    "",
                ),
                fallback=rx.cond(
                    ChatState.current_user,
                    ChatState.current_user["username"][:2].upper(),
                    "U",
                ),
                size="3",
                radius="full",
            ),
            rx.vstack(
                rx.text(
                    rx.cond(
                        ChatState.current_user,
                        ChatState.current_user["username"],
                        "User",
                    ),
                    weight="500",
                    size="3",
                ),
                rx.badge(
                    rx.cond(
                        ChatState.current_user,
                        ChatState.current_user.get("role", "user"),
                        "user",
                    ),
                    size="1",
                    color_scheme="blue",
                ),
                spacing="0",
                align_items="start",
            ),
            rx.spacer(),
            # Theme toggle
            rx.button(
                rx.cond(
                    ChatState.theme == "light",
                    rx.icon("moon", size=18),
                    rx.icon("sun", size=18),
                ),
                on_click=ChatState.toggle_theme,
                variant="ghost",
                size="2",
            ),
            # Profile menu
            rx.menu.root(
                rx.menu.trigger(
                    rx.button(
                        rx.icon("more_vertical", size=18),
                        variant="ghost",
                        size="2",
                    ),
                ),
                rx.menu.content(
                    rx.menu.item(
                        "Profile Settings",
                        on_click=ChatState.toggle_profile_modal,
                    ),
                    rx.menu.separator(),
                    rx.menu.item(
                        "Logout",
                        color_scheme="red",
                        on_click=ChatState.handle_logout,
                    ),
                ),
            ),
            class_name="w-full items-center p-4 border-b border-gray-200 dark:border-gray-700",
        ),
        
        # Search and New Chat
        rx.hstack(
            rx.input(
                placeholder="Search chats...",
                value=ChatState.search_query,
                on_change=ChatState.set_search_query,
                size="2",
                class_name="flex-1",
            ),
            rx.button(
                rx.icon("plus", size=18),
                on_click=ChatState.toggle_new_chat_modal,
                variant="soft",
                size="2",
                color_scheme="red",
                class_name="cursor-pointer",
            ),
            spacing="2",
            class_name="w-full p-4",
        ),
        
        # Room List
        rx.vstack(
            rx.cond(
                ChatState.rooms.length() > 0,
                rx.foreach(
                    ChatState.rooms,
                    room_item,
                ),
                # Empty state
                rx.vstack(
                    rx.icon("message_circle", size=48, class_name="text-gray-400"),
                    rx.text(
                        "No chats yet",
                        weight="500",
                        class_name="text-gray-500",
                    ),
                    rx.text(
                        "Start a conversation",
                        size="1",
                        class_name="text-gray-400 text-center",
                    ),
                    spacing="2",
                    class_name="items-center py-12",
                ),
            ),
            spacing="2",
            class_name="w-full px-4 overflow-y-auto flex-1",
        ),
        
        spacing="0",
        class_name="w-full lg:w-80 h-screen bg-white dark:bg-gray-800 border-r border-gray-200 dark:border-gray-700 flex-shrink-0",
    )