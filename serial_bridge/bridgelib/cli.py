import os
import sys
import logging
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from typing import Optional, Dict, Union, Any, List
from .encoder_data import make_encoders, both_encoders_from_json_string
from .transport_lf import CliTransport


class CliRequest:
    def __init__(self, command_string: str, args: List[str]):
        self.command_string = command_string
        self.args = args


class CliOkResponse:
    def __init__(self, text: str = "No Text"):
        self.tag = "OK"
        self.text = text


class CliErrorResponse:
    def __init__(self, text: str):
        self.tag = "ERROR"
        self.text = text


class CliJsonResponse:

    @staticmethod
    def create_json_response(json_string: str):
        pass

    def __init__(self, text: str):
        self.tag = "JSON"
        self.text = text
        self.both_encoders = both_encoders_from_json_string(text)
        # self.json_dict = json.loads(text)


class CliInterface:

    @staticmethod
    def parse_response(respbytes: bytes) -> CliOkResponse | CliErrorResponse | CliJsonResponse:
        response_str = respbytes.decode('utf-8')
        if response_str[0:1] == "J":
            return CliJsonResponse(response_str[1:])
        elif response_str[0:3] == "POK":
            return CliOkResponse(response_str)
        elif response_str[0:6] == "PERROR":
            return CliErrorResponse(response_str)
        else:
            return CliErrorResponse(f"Unrecognizable string ")

    @staticmethod
    def parse_request(reqbytes: bytes) -> CliRequest:
        reqstr = reqbytes.decode('utf-8')
        splits = reqstr.split(" ")
        return CliRequest(splits[0], splits[1:])

    def __init__(self, protocol: CliTransport):
        self.call_id = 0
        self.protocol = protocol

    async def cli_call(self, command_string: str) -> CliOkResponse | CliErrorResponse | CliJsonResponse:
        reqbytes = f"{command_string}".encode('utf-8')
        await self.protocol.write_message(reqbytes)
        logging.debug(f"host sent {command_string}")
        responsebytes = await self.protocol.read_message()
        response_str = responsebytes.decode('utf-8')
        return self.parse_response(responsebytes)

    async def rpm_call(self, left_rpm: float, right_rpm: float) -> CliOkResponse | CliErrorResponse:
        p = {'left_rpm': left_rpm, 'right_rpm': right_rpm}
        resp = await self.cli_call(f"rpm {left_rpm} {right_rpm}")
        return resp

    async def pwm_call(self, left_percent: float, right_percent: float):
        response = await self.cli_call(f"pwm {left_percent} {right_percent}")
        return response

    async def read_encoder_call(self, n: int):
        response = await self.cli_call(f"e")
        print(f"{response}")
        return response

    async def echo_call(self, text: str):
        response = await self.cli_call(f"echo {text}")
        return response


if __name__ == "__main__":
    def main():
        pass


    main()
