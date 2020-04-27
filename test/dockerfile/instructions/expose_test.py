from test.instructions import *
from test.dockerfile.instructions import InstructionTest


class ExposeTest(InstructionTest):
    def test_simple(self):
        instruction = Expose('80')

        expected = dict(ports=["80"])
        self.typical_positive_instruction_assertions(instruction, expected)

    def test_multiple_ports(self):
        instruction = Expose('80 90')

        expected = dict(ports=["80", "90"])
        self.typical_positive_instruction_assertions(instruction, expected)

    def test_multiple_ports_with_protocols(self):
        instruction = Expose('80 90/tcp 100/udp')

        expected = dict(ports=["80", "90/tcp", "100/udp"])
        self.typical_positive_instruction_assertions(instruction, expected)
