"""Login page."""

import reflex as rx
from ..state.auth_state import AuthState


def login_page() -> rx.Component:
    """Render login page."""
    return rx.box(
        rx.center(
            rx.vstack(
                # Logo/Header
                rx.heading(
                    "Welcome Back",
                    size="9",
                    weight="bold",
                    class_name="text-red-600",
                ),
                rx.text(
                    "Sign in to continue to your chats",
                    class_name="text-gray-500 mb-6",
                ),
                
                # Error message
                rx.cond(
                    AuthState.error_message,
                    rx.callout(
                        AuthState.error_message,
                        icon="triangle_alert",
                        color_scheme="red",
                        class_name="mb-4 w-full",
                    ),
                ),
                
                # Success message
                rx.cond(
                    AuthState.success_message,
                    rx.callout(
                        AuthState.success_message,
                        icon="circle_check",
                        color_scheme="green",
                        class_name="mb-4 w-full",
                    ),
                ),
                
                # Login Form
                rx.vstack(
                    rx.input(
                        placeholder="Username",
                        type="text",
                        value=AuthState.login_email,
                        on_change=AuthState.set_login_email,
                        size="3",
                        class_name="w-full",
                    ),
                    rx.input(
                        placeholder="Password",
                        type="password",
                        value=AuthState.login_password,
                        on_change=AuthState.set_login_password,
                        # FIX: Added False case to rx.cond
                        on_key_down=lambda key: rx.cond(
                            key == "Enter",
                            AuthState.handle_login,
                            rx.console_log("key_ignored"),
                        ),
                        size="3",
                        class_name="w-full",
                    ),
                    rx.button(
                        rx.cond(
                            AuthState.is_loading,
                            rx.hstack(
                                rx.spinner(size="3"),
                                rx.text("Signing in..."),
                                spacing="2",
                            ),
                            rx.text("Sign In"),
                        ),
                        on_click=AuthState.handle_login,
                        size="3",
                        color_scheme="red",
                        disabled=AuthState.is_loading,
                        class_name="w-full cursor-pointer",
                    ),
                    spacing="4",
                    class_name="w-full",
                ),
                
                # Divider
                rx.divider(class_name="my-6"),
                
                # Sign up link
                rx.hstack(
                    rx.text("Don't have an account?", class_name="text-gray-500"),
                    rx.link(
                        "Sign up",
                        href="/signup",
                        class_name="text-red-600 font-medium hover:underline",
                    ),
                    spacing="2",
                ),
                
                spacing="4",
                class_name="w-full max-w-md p-8 bg-white dark:bg-gray-800 rounded-xl shadow-lg border border-gray-200 dark:border-gray-700",
            ),
            class_name="min-h-screen",
        ),
        class_name="bg-gray-50 dark:bg-gray-900 p-4",
    )