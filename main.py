import pyotp
import os

from ulauncher.api.client.Extension import Extension
from ulauncher.api.client.EventListener import EventListener
from ulauncher.api.shared.event import KeywordQueryEvent, ItemEnterEvent
from ulauncher.api.shared.item.ExtensionResultItem import ExtensionResultItem
from ulauncher.api.shared.action.RenderResultListAction import RenderResultListAction
from ulauncher.api.shared.action.CopyToClipboardAction import CopyToClipboardAction
from ulauncher.api.shared.action.ExtensionCustomAction import ExtensionCustomAction

TOTP_HOME = os.path.join(os.path.expanduser("~"), ".config", "totp")
SERVICES_HOME = os.path.join(TOTP_HOME, "services")
ICONS_HOME = os.path.join(TOTP_HOME, "images")


def get_services():
    return os.listdir(SERVICES_HOME)


def get_otp(service):
    service_file = os.path.join(SERVICES_HOME, service)
    with open(service_file, "r") as f:
        secret = f.read().replace("\n", "")
    print(secret)
    totp = pyotp.TOTP(secret)
    return totp.now()


class TotpExtension(Extension):

    def __init__(self):
        super().__init__()
        self.subscribe(KeywordQueryEvent, KeywordQueryEventListener())
        self.subscribe(ItemEnterEvent, ItemEnterEventListener())


class KeywordQueryEventListener(EventListener):

    def on_event(self, event, extension):
        items = []
        services = get_services()
        for service in services:
            data = {"service": service}
            items.append(ExtensionResultItem(icon=f'{ICONS_HOME}/{service}.png',
                                             name=service,
                                             on_enter=ExtensionCustomAction(data, keep_app_open=True)))

        return RenderResultListAction(items)


class ItemEnterEventListener(EventListener):

    def on_event(self, event, extension):

        data = event.get_data()
        service = data["service"]
        otp = get_otp(service)

        return CopyToClipboardAction(otp)


if __name__ == '__main__':
    TotpExtension().run()
