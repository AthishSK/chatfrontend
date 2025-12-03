"""Main chat dashboard page."""

import reflex as rx
from ..state.chat_state import ChatState
from ..components.sidebar import sidebar
from ..components.chat_area import chat_area
from ..components.modals import new_chat_modal, profile_modal


def chat_page() -> rx.Component:
    """Main chat dashboard."""
    return rx.fragment(
        # Check auth on mount
        rx.script("""
            const token = document.cookie.split('; ').find(row => row.startsWith('access_token='));
            if (!token) {
                window.location.href = '/login';
            }
        """),
        
        rx.box(
            # Error notification
            rx.cond(
                ChatState.error_message,
                rx.box(
                    rx.callout(
                        ChatState.error_message,
                        icon="triangle_alert",
                        color_scheme="red",
                        on_click=ChatState.clear_messages,
                    ),
                    class_name="fixed top-4 right-4 z-50 max-w-md animate-slide-in cursor-pointer",
                ),
            ),
            
            # Success notification
            rx.cond(
                ChatState.success_message,
                rx.box(
                    rx.callout(
                        ChatState.success_message,
                        icon="check_circle",
                        color_scheme="green",
                        on_click=ChatState.clear_messages,
                    ),
                    class_name="fixed top-4 right-4 z-50 max-w-md animate-slide-in cursor-pointer",
                ),
            ),
            
            # Main layout
            rx.box(
                # Sidebar - Hidden on mobile unless toggled
                rx.box(
                    sidebar(),
                    class_name=rx.cond(
                        ChatState.show_sidebar,
                        "fixed inset-0 z-40 lg:relative lg:z-auto",
                        "hidden lg:block",
                    ),
                ),
                # Overlay for mobile
                rx.cond(
                    ChatState.show_sidebar,
                    rx.box(
                        on_click=ChatState.toggle_sidebar,
                        class_name="fixed inset-0 bg-black/50 z-30 lg:hidden",
                    ),
                ),
                # Chat area
                rx.box(
                    chat_area(),
                    class_name="flex-1 h-screen",
                ),
                class_name="flex w-full h-screen overflow-hidden",
            ),
            
            # Modals
            new_chat_modal(),
            profile_modal(),
            
            class_name="w-full h-screen bg-gray-50 dark:bg-gray-900",
            on_mount=[ChatState.check_auth, ChatState.load_rooms, ChatState.load_users],
        ),
    )