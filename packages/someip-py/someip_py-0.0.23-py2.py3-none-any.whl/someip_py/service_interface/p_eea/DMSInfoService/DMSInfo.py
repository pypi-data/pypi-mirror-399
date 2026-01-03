from someip_py.codec import *


class IdtDMSInfoProtoHeader(SomeIpPayload):

    IdtDMSInfoTimeStamp: Uint64

    IdtDMSInfoTransId: Uint32

    IdtDMSInfoLength: Uint32

    IdtDMSInfoFieldId: Uint8

    IdtDMSInfoProtoVersion: Uint8

    IdtDMSInfoReserved: SomeIpFixedSizeArray[Uint8]

    def __init__(self):

        self.IdtDMSInfoTimeStamp = Uint64()

        self.IdtDMSInfoTransId = Uint32()

        self.IdtDMSInfoLength = Uint32()

        self.IdtDMSInfoFieldId = Uint8()

        self.IdtDMSInfoProtoVersion = Uint8()

        self.IdtDMSInfoReserved = SomeIpFixedSizeArray(Uint8, size=6)


class IdtDMSInfoKls(SomeIpPayload):
    _has_dynamic_size = True

    IdtDMSInfoProtoHeader: IdtDMSInfoProtoHeader

    IdtDMSInfoProtoPayload: SomeIpDynamicSizeArray[Uint8]

    def __init__(self):

        self.IdtDMSInfoProtoHeader = IdtDMSInfoProtoHeader()

        self.IdtDMSInfoProtoPayload = SomeIpDynamicSizeArray(Uint8)


class IdtDMSInfo(SomeIpPayload):

    IdtDMSInfo: IdtDMSInfoKls

    def __init__(self):

        self.IdtDMSInfo = IdtDMSInfoKls()
