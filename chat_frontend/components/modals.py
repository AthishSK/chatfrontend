"""Modal components for new chat and profile."""

import reflex as rx
from ..state.chat_state import ChatState
from ..state.profile_state import ProfileState


def new_chat_modal() -> rx.Component:
    """Modal for creating new chat or DM."""
    return rx.dialog.root(
        rx.dialog.content(
            rx.dialog.title("New Chat"),
            rx.dialog.description(
                "Start a direct message or create a group chat"
            ),
            
            rx.tabs.root(
                rx.tabs.list(
                    rx.tabs.trigger("Direct Message", value="dm"),
                    rx.tabs.trigger("New Group", value="group"),
                ),
                
                # DM Tab
                rx.tabs.content(
                    rx.vstack(
                        rx.text("Select a user to message:", size="2", weight="500"),
                        rx.cond(
                            ChatState.users.length() > 0,
                            rx.vstack(
                                rx.foreach(
                                    ChatState.users,
                                    lambda user: rx.box(
                                        rx.hstack(
                                            rx.avatar(
                                                src=user.get("avatar_url"),
                                                fallback=user["username"][:2].upper(),
                                                size="2",
                                            ),
                                            rx.vstack(
                                                rx.text(user["username"], weight="500"),
                                                rx.text(
                                                    user.get("bio", "No bio"),
                                                    size="1",
                                                    class_name="text-gray-500",
                                                ),
                                                spacing="0",
                                                align_items="start",
                                            ),
                                            spacing="3",
                                            class_name="w-full items-center",
                                        ),
                                        on_click=lambda username=user["username"]: ChatState.start_dm(username),
                                        class_name="p-3 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800 cursor-pointer transition-colors",
                                    ),
                                ),
                                spacing="2",
                                class_name="max-h-96 overflow-y-auto w-full",
                            ),
                            rx.text("No users available", class_name="text-gray-500"),
                        ),
                        spacing="3",
                        class_name="w-full",
                    ),
                    value="dm",
                ),
                
                # Group Tab
                rx.tabs.content(
                    rx.vstack(
                        rx.input(
                            placeholder="Group name",
                            value=ChatState.new_room_name,
                            on_change=ChatState.set_new_room_name,
                            size="3",
                            class_name="w-full",
                        ),
                        rx.text("Select members:", size="2", weight="500", class_name="mt-4"),
                        rx.cond(
                            ChatState.users.length() > 0,
                            rx.vstack(
                                rx.foreach(
                                    ChatState.users,
                                    lambda user: rx.box(
                                        rx.hstack(
                                            rx.checkbox(
                                                checked=ChatState.selected_members.contains(user["username"]),
                                                on_change=lambda checked, username=user["username"]: ChatState.toggle_member(username),
                                            ),
                                            rx.avatar(
                                                src=user.get("avatar_url"),
                                                fallback=user["username"][:2].upper(),
                                                size="2",
                                            ),
                                            rx.text(user["username"], weight="500"),
                                            spacing="3",
                                            class_name="w-full items-center",
                                        ),
                                        class_name="p-3 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800 cursor-pointer transition-colors",
                                    ),
                                ),
                                spacing="2",
                                class_name="max-h-64 overflow-y-auto w-full",
                            ),
                            rx.text("No users available", class_name="text-gray-500"),
                        ),
                        rx.button(
                            "Create Group",
                            on_click=ChatState.create_new_room,
                            color_scheme="red",
                            size="3",
                            class_name="w-full cursor-pointer mt-4",
                            disabled=ChatState.new_room_name == "",
                        ),
                        spacing="3",
                        class_name="w-full",
                    ),
                    value="group",
                ),
                
                default_value="dm",
                class_name="w-full",
            ),
            
            rx.dialog.close(
                rx.button(
                    "Cancel",
                    variant="soft",
                    color_scheme="gray",
                    class_name="cursor-pointer",
                ),
            ),
            
            class_name="max-w-md",
        ),
        open=ChatState.show_new_chat_modal,
        on_open_change=ChatState.toggle_new_chat_modal,
    )


def profile_modal() -> rx.Component:
    """Modal for editing user profile."""
    return rx.dialog.root(
        rx.dialog.content(
            rx.dialog.title("Profile Settings"),
            rx.dialog.description("Update your profile information"),
            
            rx.vstack(
                # Avatar section
                rx.vstack(
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
                        size="8",
                        radius="full",
                    ),
                    rx.upload(
                        rx.button(
                            rx.icon("upload", size=16),
                            "Change Avatar",
                            variant="soft",
                            size="2",
                            class_name="cursor-pointer",
                        ),
                        accept={"image/*": [".jpg", ".jpeg", ".png"]},
                        max_files=1,
                        on_drop=ProfileState.handle_upload,
                    ),
                    spacing="3",
                    class_name="items-center mb-6",
                ),
                
                # Bio section
                rx.vstack(
                    rx.text("Bio:", size="2", weight="500"),
                    rx.text_area(
                        placeholder="Tell us about yourself...",
                        value=ProfileState.edit_bio,
                        on_change=ProfileState.set_edit_bio,
                        rows=3,
                        class_name="w-full",
                    ),
                    rx.button(
                        "Update Bio",
                        on_click=ProfileState.update_bio,
                        color_scheme="red",
                        size="2",
                        class_name="w-full cursor-pointer",
                    ),
                    spacing="2",
                    class_name="w-full",
                ),
                
                rx.divider(class_name="my-4"),
                
                # Password section
                rx.vstack(
                    rx.text("Change Password:", size="2", weight="500"),
                    rx.input(
                        placeholder="New password",
                        type="password",
                        value=ProfileState.new_password,
                        on_change=ProfileState.set_new_password,
                        size="2",
                        class_name="w-full",
                    ),
                    rx.input(
                        placeholder="Confirm password",
                        type="password",
                        value=ProfileState.confirm_password,
                        on_change=ProfileState.set_confirm_password,
                        size="2",
                        class_name="w-full",
                    ),
                    rx.button(
                        "Update Password",
                        on_click=ProfileState.update_password,
                        color_scheme="red",
                        size="2",
                        class_name="w-full cursor-pointer",
                    ),
                    spacing="2",
                    class_name="w-full",
                ),
                
                spacing="4",
                class_name="w-full",
            ),
            
            rx.dialog.close(
                rx.button(
                    "Close",
                    variant="soft",
                    color_scheme="gray",
                    class_name="cursor-pointer mt-4",
                ),
            ),
            
            class_name="max-w-md",
        ),
        open=ChatState.show_profile_modal,
        on_open_change=ChatState.toggle_profile_modal,
    )