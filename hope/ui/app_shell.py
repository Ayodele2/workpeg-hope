
"""HOPE application navigation and shared scrolling shell."""

from workpeg.ui import (
    Shell,
    Outlet,
    ListView,
    Text,
    biz_url,
    set_color_scheme,
    store,
)

from workpeg.ui.scaffold import Scaffold, NavItem, NavSection, NavFixed


class AppShell(Shell):

    async def on_mount(self):
        set_color_scheme("system")

    def build(self):
        return Scaffold(
            NavSection(
                "Hotel Operations",
                NavItem(
                    "Response Overview",
                    biz_url("/"),
                    icon="layout-dashboard",
                ),
                NavItem(
                    "Guest Emergencies",
                    biz_url("/dispatch"),
                    icon="alert-triangle",
                ),
                NavItem(
                    "Medical Resources",
                    biz_url("/resources"),
                    icon="building-2",
                ),
            ),
            fixed=NavFixed(
                NavItem(
                    "Hotel Home",
                    biz_url("/"),
                    icon="home",
                ),
            ),
            top_nav=Text(
                store.page_title,
                weight="semibold",
            ),
            main=ListView(
                Outlet(),
                height="calc(100vh - 100px)",
                width="100%",
                padding=24,
                gap=16,
            ),
        )
