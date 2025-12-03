import reflex as rx

config = rx.Config(
    app_name="chat_frontend",
    frontend_port=3005,
    backend_port=8005,
    plugins=[
        rx.plugins.TailwindV4Plugin(),
        # Add this to silence the warning:
        rx.plugins.sitemap.SitemapPlugin(), 
    ],
)