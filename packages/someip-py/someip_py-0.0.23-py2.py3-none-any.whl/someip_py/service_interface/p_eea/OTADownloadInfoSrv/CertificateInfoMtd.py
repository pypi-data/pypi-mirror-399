from someip_py.codec import *


class OTASignatureCertificateStructKls(SomeIpPayload):

    OTASignatureCertificate: SomeIpDynamicSizeString

    OCSPRespData: SomeIpDynamicSizeString

    def __init__(self):

        self.OTASignatureCertificate = SomeIpDynamicSizeString()

        self.OCSPRespData = SomeIpDynamicSizeString()


class OTASignatureCertificateStruct(SomeIpPayload):

    OTASignatureCertificateStruct: OTASignatureCertificateStructKls

    def __init__(self):

        self.OTASignatureCertificateStruct = OTASignatureCertificateStructKls()


class OTASignatureCertificateRespStructKls(SomeIpPayload):

    Status: SomeIpDynamicSizeString

    RetVal: Uint8

    def __init__(self):

        self.Status = SomeIpDynamicSizeString()

        self.RetVal = Uint8()


class OTASignatureCertificateRespStruct(SomeIpPayload):

    OTASignatureCertificateRespStruct: OTASignatureCertificateRespStructKls

    def __init__(self):

        self.OTASignatureCertificateRespStruct = OTASignatureCertificateRespStructKls()
