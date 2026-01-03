VERSION = "0.2.0"

PROTOCOL_VERSION = 1
FEATURE_LEVEL = 2

FEATURE_OTA_FW_UPDATE = 2


def supports(dev, feat):
    return dev.get("feature_level", 0) >= feat
