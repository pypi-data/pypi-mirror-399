from someip_py.codec import *


class RVDCAssignmentNotificaitonKls(SomeIpPayload):

    Isotimestamp: SomeIpDynamicSizeString

    Newstatus: SomeIpDynamicSizeString

    Reason: SomeIpDynamicSizeString

    Maid: Uint32

    Maversion: Uint32

    def __init__(self):

        self.Isotimestamp = SomeIpDynamicSizeString()

        self.Newstatus = SomeIpDynamicSizeString()

        self.Reason = SomeIpDynamicSizeString()

        self.Maid = Uint32()

        self.Maversion = Uint32()


class RVDCAssignmentNotificaiton(SomeIpPayload):

    RVDCAssignmentNotificaiton: RVDCAssignmentNotificaitonKls

    def __init__(self):

        self.RVDCAssignmentNotificaiton = RVDCAssignmentNotificaitonKls()


class RetVal(SomeIpPayload):

    RetVal: Uint8

    def __init__(self):

        self.RetVal = Uint8()
