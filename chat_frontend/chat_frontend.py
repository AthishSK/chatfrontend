"""Main Reflex application entry point."""

import reflex as rx
from .pages import login, signup, chat


# Create the app
app = rx.App()

# Add pages
app.add_page(
    login.login_page,
    route="/",
    title="Login - Chat App",
)

app.add_page(
    login.login_page,
    route="/login",
    title="Login - Chat App",
)

app.add_page(
    signup.signup_page,
    route="/signup",
    title="Sign Up - Chat App",
)

app.add_page(
    chat.chat_page,
    route="/chat",
    title="Chat - Dashboard",
)