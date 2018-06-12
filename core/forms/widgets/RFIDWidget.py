from django.forms import widgets


class RFIDWidget(widgets.TextInput):

    change_button_text = "Enter Manually"
    allow_revert = True
    revert_button_text = "Hide Manual Input"
    scan_rfid_button_text = "Click to Scan RFID"
    template_name = "widgets/rfid.html"

    def __init__(self, attrs=None):
        # TODO: Add option to modify default values of class vars here
        super().__init__(attrs)

    def get_context(self, name, value, attrs):
        context = super(RFIDWidget, self).get_context(name, value, attrs)

        widget = context['widget']
        widget['change_button_text'] = self.change_button_text
        widget['allow_revert'] = self.allow_revert
        widget['revert_button_text'] = self.revert_button_text
        widget['scan_rfid_button_text'] = self.scan_rfid_button_text

        context['widget'] = widget
        return context
