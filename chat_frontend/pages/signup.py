"""Signup/registration page."""

import reflex as rx
from ..state.auth_state import AuthState


def signup_page() -> rx.Component:
    """Render signup page."""
    return rx.box(
        rx.center(
            rx.vstack(
                # Logo/Header
                rx.heading(
                    "Create Account",
                    size="9",
                    weight="bold",
                    class_name="text-red-600",
                ),
                rx.text(
                    "Join us and start chatting",
                    class_name="text-gray-500 mb-6",
                ),
                
                # Error message
                rx.cond(
                    AuthState.error_message,
                    rx.callout(
                        AuthState.error_message,
                        icon="triangle-alert",
                        color_scheme="red",
                        class_name="mb-4 w-full",
                    ),
                ),
                
                # Success message
                rx.cond(
                    AuthState.success_message,
                    rx.callout(
                        AuthState.success_message,
                        icon="circle-check",  # FIX: Updated icon name
                        color_scheme="green",
                        class_name="mb-4 w-full",
                    ),
                ),
                
                # Signup Form
                rx.vstack(
                    rx.input(
                        placeholder="Username",
                        type="text",
                        value=AuthState.signup_username,
                        on_change=AuthState.set_signup_username,
                        size="3",
                        class_name="w-full",
                    ),
                    rx.input(
                        placeholder="Password (min 6 characters)",
                        type="password",
                        value=AuthState.signup_password,
                        on_change=AuthState.set_signup_password,
                        size="3",
                        class_name="w-full",
                    ),
                    rx.input(
                        placeholder="Confirm password",
                        type="password",
                        value=AuthState.signup_confirm_password,
                        on_change=AuthState.set_signup_confirm_password,
                        size="3",
                        class_name="w-full",
                    ),
                    rx.button(
                        rx.cond(
                            AuthState.is_loading,
                            rx.hstack(
                                rx.spinner(size="3"),
                                rx.text("Creating account..."),
                                spacing="2",
                            ),
                            rx.text("Sign Up"),
                        ),
                        on_click=AuthState.handle_signup,
                        size="3",
                        color_scheme="red",
                        disabled=AuthState.is_loading,
                        class_name="w-full cursor-pointer",
                    ),
                    spacing="4",
                    class_name="w-full",
                ),
                
                # Terms notice
                rx.text(
                    "By signing up, you agree to our Terms and Privacy Policy",
                    size="1",
                    class_name="text-gray-500 text-center mt-4",
                ),
                
                # Divider
                rx.divider(class_name="my-6"),
                
                # Login link
                rx.hstack(
                    rx.text("Already have an account?", class_name="text-gray-500"),
                    rx.link(
                        "Sign in",
                        href="/login",
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