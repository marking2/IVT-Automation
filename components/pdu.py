import json
from paramiko import SSHClient
from .component import Component


class PDU(Component):
    MODELS = {
        "AP8953": [
            "PDU-00001-A - APC,AP8953,1PH,208V,32A,IEC IP44,3M",
            "PDU-00010-A - APC,AP8953,1PH,208V,32A,IEC IP67,3M",
            "PDU-00002-A - APC,AP8953,1PH,208V,32A,NEMA,3M",
            "PDU-00018-A - APC,AP8953X634,1PH,208V,32A,IEC,4.5M",
        ],
        "AP8981": [
            "PDU-00003-A - APC,AP8981X633,3PH,400V,16A,IEC IP44,3M",
            "PDU-00006-A - APC,AP8981,3PH,400V,16A,IEC IP67,3M",
            "PDU-00019-A - APC,AP8981X634,3PH,S,400V,16A,IEC,4.5M",
            "PDU-00023-A - APC,AP8981X814,3PH,400V,16A,IEC IP44,4.5M",
        ],
        "AP8965": [
            "PDU-00008-A - APC,AP8965,3PH,208V,16A,IEC IP67,3M",
            "PDU-00004-A - APC,AP8965X633,3PH,208V,16A,NEMA,3M",
            "PDU-00020-A - APC,AP8965X634,3PH,D,208V,16A,NEMA,4.5M",
            "PDU-00024-A - APC,AP8965X813,3PH,208V,30A,NEMA,4.5M",
        ],
        "AP8941": [
            "PDU-00013-A - APC,AP8941,1PH,200V,30A,NEMA",
            "PDU-00021-A - APC,AP8941X634,1PH,200V,30A,NEMA,4.5M",
        ],
        "Other": [
            "PDU-00086 - PDU,APC,APDU9953,1PH,220V-240V,32A,IEC-309,3.0M",
            "PDU-00087 - PDU,APC,APDU9941,1PH,200V-240V,24A,NEMA L6-30P,3.0M",
            "PDU-00088 - PDU,APC,APDU9981EU3,3PH,380V-415V,16A,IEC-309,3.5M",
            "PDU-00089 - PDU,APC,APDU9965,3PH,208V,24A,NEMA L21-30P,3.5M",
            "PDU-00091 - PDU,APC,APDU9967,3PH,208V,IEC 309 60A 3P+PE,1.8M",
        ]
    }

    def __init__(self, connection: SSHClient, part_name: int):
        self.part_name = part_name
        self.metadata = self._set_metadata(connection)
        super(PDU, self).__init__(connection, part_name)

    def _set_metadata(self, connection) -> json:
        _, stdout, _ = connection.exec_command(self._get_commands()[0].format(self.part_name))
        stdout_as_string = stdout.read()
        return json.loads(stdout_as_string)

    def get_name(self) -> str:
        return "pdu"

    def _get_serial(self) -> str:
        return self.metadata["pdu"]["serial"]

    def get_model_parent(self) -> str:
        return "PDU"

    def _get_model(self) -> str:
        pdu_part_model = self.metadata.get("pdu").get("model")
        parts = pdu_part_model.split('X')
        requested_part_list = self.MODELS.get(parts[0], "Other")
        for value in requested_part_list:
            if value.__contains__(pdu_part_model):
                return value

    def _get_commands(self) -> [str]:
        return ["/opt/infinidat/sa-utils/utils/pdu-tool.py -p {} -c about"]

    def get_rc_parent(self) -> str:
        return "Other (Add in Comment)"

    def get_summary(self) -> str:
        return "PDU-{} replacement".format(self.part_name)

    def get_original_location(self) -> str:
        return "PDU-{}".format(self.part_name)
