from workpeg.ui import (
    App, Padding, Column, Row, Container, Expanded, Text, Button, Icon,
    biz_url, navigate, set_title, store,
)


class HomePage(App):
    def on_mount(self):
        store.page_title = "Home"
        set_title("Home")

    def open_customers(self):
        navigate(biz_url("/customers"))

    def build(self):
        return Padding(
            Column(
                Column(
                    Text(f"Welcome to {store.business}", variant="heading"),
                    Text("Keep track of the people you sell to.",
                         variant="muted"),
                    gap=4,
                ),
                Container(
                    Row(
                        Icon("users", size=24),
                        Expanded(
                            Column(
                                Text("Customers", weight="semibold"),
                                Text("Leads, active accounts and churn.",
                                     variant="caption"),
                                gap=4,
                            ),
                        ),
                        Button("Open", variant="outline-gray",
                               icon="arrow-right", icon_position="right",
                               on_click=self.open_customers),
                        align="center", gap=16,
                    ),
                    variant="card", padding=24,
                ),
                gap=24,
            ),
            all=24,
        )
