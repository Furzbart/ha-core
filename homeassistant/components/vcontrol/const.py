"""Constants for the Viessmann vcontrol integration."""

DOMAIN = "vcontrol"


SENSORS = {
    "vcontrol_aussentemperatur": {
        "name": "Aussentemperatur",
        "type": "temperature",
        "unit": "°C",
    },
    "vcontrol_druckHeissgas": {
        "name": "DruckHeissgas",
        "type": "pressure",
        "unit": "bar",
    },
    "vcontrol_druckSauggas": {
        "name": "DruckSauggas",
        "type": "pressure",
        "unit": "bar",
    },
    "vcontrol_vorlauftempSek": {
        "name": "VorlauftempSek",
        "type": "temperature",
        "unit": "°C",
    },
    "vcontrol_ruecklauftempSek": {
        "name": "RuecklauftempSek",
        "type": "temperature",
        "unit": "°C",
    },
    "vcontrol_vorlauftempSollHK1": {
        "name": "VorlauftempSollHK1",
        "type": "temperature",
        "unit": "°C",
    },
}
