from someip_py.codec import *


class PostInstallationInfoStructKls(SomeIpPayload):

    Installationorder: SomeIpDynamicSizeString

    Isotimestamp: SomeIpDynamicSizeString

    Newstatus: SomeIpDynamicSizeString

    Reason: SomeIpDynamicSizeString

    def __init__(self):

        self.Installationorder = SomeIpDynamicSizeString()

        self.Isotimestamp = SomeIpDynamicSizeString()

        self.Newstatus = SomeIpDynamicSizeString()

        self.Reason = SomeIpDynamicSizeString()


class PostInstallationInfoStruct(SomeIpPayload):

    PostInstallationInfoStruct: PostInstallationInfoStructKls

    def __init__(self):

        self.PostInstallationInfoStruct = PostInstallationInfoStructKls()


class ConnectionStatusStructKls(SomeIpPayload):

    Available: Uint8

    RetVal: Uint8

    def __init__(self):

        self.Available = Uint8()

        self.RetVal = Uint8()


class ConnectionStatusStruct(SomeIpPayload):

    ConnectionStatusStruct: ConnectionStatusStructKls

    def __init__(self):

        self.ConnectionStatusStruct = ConnectionStatusStructKls()
