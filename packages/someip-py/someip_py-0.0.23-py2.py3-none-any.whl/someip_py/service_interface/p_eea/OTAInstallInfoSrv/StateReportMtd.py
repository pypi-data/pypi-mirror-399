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
