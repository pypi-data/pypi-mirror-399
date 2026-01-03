from someip_py.codec import *


class ExceptionuniquesourceidStruct(SomeIpPayload):

    Installationorder: SomeIpDynamicSizeString

    Clientversion: SomeIpDynamicSizeString

    def __init__(self):

        self.Installationorder = SomeIpDynamicSizeString()

        self.Clientversion = SomeIpDynamicSizeString()


class ExceptionmessageStruct(SomeIpPayload):

    Activity: SomeIpDynamicSizeString

    Action: SomeIpDynamicSizeString

    Exception: SomeIpDynamicSizeString

    LogParams: SomeIpDynamicSizeString

    def __init__(self):

        self.Activity = SomeIpDynamicSizeString()

        self.Action = SomeIpDynamicSizeString()

        self.Exception = SomeIpDynamicSizeString()

        self.LogParams = SomeIpDynamicSizeString()


class ExceptionreportsStruct(SomeIpPayload):

    ExceptionuniquesourceidStruct: ExceptionuniquesourceidStruct

    Isotimestamp: SomeIpDynamicSizeString

    Issuerid: SomeIpDynamicSizeString

    FileName: SomeIpDynamicSizeString

    EcuAddress: SomeIpDynamicSizeString

    KeyName: SomeIpDynamicSizeString

    KeyValue: SomeIpDynamicSizeString

    DataBlock: SomeIpDynamicSizeString

    ExceptionmessageStruct: ExceptionmessageStruct

    def __init__(self):

        self.ExceptionuniquesourceidStruct = ExceptionuniquesourceidStruct()

        self.Isotimestamp = SomeIpDynamicSizeString()

        self.Issuerid = SomeIpDynamicSizeString()

        self.FileName = SomeIpDynamicSizeString()

        self.EcuAddress = SomeIpDynamicSizeString()

        self.KeyName = SomeIpDynamicSizeString()

        self.KeyValue = SomeIpDynamicSizeString()

        self.DataBlock = SomeIpDynamicSizeString()

        self.ExceptionmessageStruct = ExceptionmessageStruct()


class InstallStatusStructKls(SomeIpPayload):

    Exceptionreportmsgremaining: Uint16

    ExceptionreportsStruct: ExceptionreportsStruct

    def __init__(self):

        self.Exceptionreportmsgremaining = Uint16()

        self.ExceptionreportsStruct = ExceptionreportsStruct()


class InstallStatusStruct(SomeIpPayload):

    InstallStatusStruct: InstallStatusStructKls

    def __init__(self):

        self.InstallStatusStruct = InstallStatusStructKls()
