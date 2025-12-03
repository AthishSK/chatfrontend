"""WhatsApp-style message bubble component - FIXED ALIGNMENT."""

import reflex as rx
from ..state.chat_state import ChatState


def message_status_indicator(status: str, is_read: bool) -> rx.Component:
    """Show message status icon."""
    return rx.cond(
        status == "sending",
        rx.spinner(size="1", class_name="text-gray-400"),
        rx.cond(
            status == "failed",
            rx.icon("circle-alert", size=14, class_name="text-red-500"),
            rx.cond(
                is_read,
                rx.icon("check-check", size=14, class_name="text-blue-500"),
                rx.icon("check", size=14, class_name="text-gray-500"),
            ),
        ),
    )


def message_bubble(message: dict) -> rx.Component:
    """
    Render a single message bubble with WhatsApp-style alignment.
    
    CRITICAL FIX: Properly align messages based on user_id comparison.
    """
    # FIXED: Compare message user_id with current_user id
    is_own = message["user_id"] == ChatState.current_user["id"]
    
    return rx.box(
        rx.cond(
            is_own,
            # ===== OWN MESSAGE (RIGHT-ALIGNED, GREEN) =====
            rx.hstack(
                rx.spacer(),
                rx.vstack(
                    rx.box(
                        # Message content with markdown
                        rx.markdown(
                            message["content"],
                            class_name="text-white text-sm leading-relaxed",
                        ),
                        # Attachment if present
                        rx.cond(
                            message.get("attachment_url"),
                            rx.image(
                                src=f"http://127.0.0.1:8020{message['attachment_url']}",
                                class_name="mt-2 rounded-lg max-w-xs",
                            ),
                        ),
                        # Timestamp and status row
                        rx.hstack(
                            rx.spacer(),
                            rx.text(
                                message["timestamp"],
                                size="1",
                                class_name="text-white/70",
                            ),
                            message_status_indicator(
                                message.get("status", "sent"),
                                message.get("is_read", False)
                            ),
                            spacing="1",
                            class_name="mt-1 items-center",
                        ),
                        class_name="px-3 py-2 bg-green-600 rounded-lg rounded-br-none max-w-md shadow-sm relative group",
                    ),
                    # Copy button (appears on hover)
                    rx.button(
                        rx.icon("copy", size=12),
                        on_click=lambda: ChatState.copy_message(message["content"]),
                        variant="ghost",
                        size="1",
                        class_name="absolute -top-6 right-0 opacity-0 group-hover:opacity-100 transition-opacity bg-gray-700 text-white",
                    ),
                    spacing="0",
                    align_items="end",
                    class_name="relative max-w-[70%]",
                ),
                spacing="2",
                class_name="w-full justify-end mb-1",
            ),
            # ===== OTHER'S MESSAGE (LEFT-ALIGNED, WHITE) =====
            rx.hstack(
                rx.avatar(
                    src=f"http://127.0.0.1:8020{message.get('avatar_url', '')}",
                    fallback=message["user"].to(str)[:2].upper(),
                    size="2",
                    radius="full",
                    class_name="flex-shrink-0",
                ),
                rx.vstack(
                    # Username
                    rx.text(
                        message["user"],
                        size="1",
                        weight="medium",
                        class_name="text-green-600 mb-1",
                    ),
                    rx.box(
                        # Message content with markdown
                        rx.markdown(
                            message["content"],
                            class_name="text-gray-900 dark:text-gray-100 text-sm leading-relaxed",
                        ),
                        # Attachment if present
                        rx.cond(
                            message.get("attachment_url"),
                            rx.image(
                                src=f"http://127.0.0.1:8020{message['attachment_url']}",
                                class_name="mt-2 rounded-lg max-w-xs",
                            ),
                        ),
                        # Timestamp
                        rx.text(
                            message["timestamp"],
                            size="1",
                            class_name="text-gray-500 mt-1",
                        ),
                        class_name="px-3 py-2 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg rounded-bl-none max-w-md shadow-sm relative group",
                    ),
                    # Copy button (appears on hover)
                    rx.button(
                        rx.icon("copy", size=12),
                        on_click=lambda: ChatState.copy_message(message["content"]),
                        variant="ghost",
                        size="1",
                        class_name="absolute -top-6 right-0 opacity-0 group-hover:opacity-100 transition-opacity bg-gray-700 text-white",
                    ),
                    spacing="0",
                    align_items="start",
                    class_name="relative max-w-[70%]",
                ),
                spacing="2",
                class_name="w-full justify-start mb-1",
            ),
        ),
        class_name="w-full px-4 animate-slide-up",
    )