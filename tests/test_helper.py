import unittest
from src.helper import *
from src.OP_CODE.op_code_implementation import handle_opcode_stack


class TestHelper(unittest.TestCase):
    def test_OP_PUSHBYTES(self):
        opcode = "OP_PUSHBYTES_72"
        asm_instruction_in_list = [
            "OP_PUSHBYTES_72",
            "30450221009eb05e52c05023c4239806f6ad4bf5595e6d81fee329e3794f38259170e4d8b302200a1f7174be46c657dab0449ecaa9002a4480a7ba6bef26492e2990e6426fe55a01",
        ]
        stack = []
        index = 0
        expectedOutput = 1, [
            "30450221009eb05e52c05023c4239806f6ad4bf5595e6d81fee329e3794f38259170e4d8b302200a1f7174be46c657dab0449ecaa9002a4480a7ba6bef26492e2990e6426fe55a01"
        ]
        self.assertEqual(
            handle_opcode_stack(opcode, stack, index, asm_instruction_in_list),
            expectedOutput,
        )

    def test_OP_EQUALVERIFY(self):
        opcode = "OP_EQUALVERIFY"
        asm_instruction_in_list = [""]
        stack = [
            "30450221009eb05e52c05023c4239806f6ad4bf5595e6d81fee329e3794f38259170e4d8b302200a1f7174be46c657dab0449ecaa9002a4480a7ba6bef26492e2990e6426fe55a01",
            "30450221009eb05e52c05023c4239806f6ad4bf5595e6d81fee329e3794f38259170e4d8b302200a1f7174be46c657dab0449ecaa9002a4480a7ba6bef26492e2990e6426fe55a01",
        ]
        index = 0
        expectedOutput = (0, [])
        self.assertEqual(
            handle_opcode_stack(opcode, stack, index, asm_instruction_in_list),
            expectedOutput,
        )

    def test_OP_DUP(self):
        opcode = "OP_DUP"
        asm_instruction_in_list = [""]
        stack = [
            "30450221009eb05e52c05023c4239806f6ad4bf5595e6d81fee329e3794f38259170e4d8b302200a1f7174be46c657dab0449ecaa9002a4480a7ba6bef26492e2990e6426fe55a01"
        ]
        index = 0
        expectedOutput = (
            0,
            [
                "30450221009eb05e52c05023c4239806f6ad4bf5595e6d81fee329e3794f38259170e4d8b302200a1f7174be46c657dab0449ecaa9002a4480a7ba6bef26492e2990e6426fe55a01",
                "30450221009eb05e52c05023c4239806f6ad4bf5595e6d81fee329e3794f38259170e4d8b302200a1f7174be46c657dab0449ecaa9002a4480a7ba6bef26492e2990e6426fe55a01",
            ],
        )
        self.assertEqual(
            handle_opcode_stack(opcode, stack, index, asm_instruction_in_list),
            expectedOutput,
        )

    def test_OP_HASH160(self):
        opcode = "OP_HASH160"
        asm_instruction_in_list = [""]
        stack = [
            "30450221009eb05e52c05023c4239806f6ad4bf5595e6d81fee329e3794f38259170e4d8b302200a1f7174be46c657dab0449ecaa9002a4480a7ba6bef26492e2990e6426fe55a01"
        ]
        index = 0
        expectedOutput = (0, ["42bd173301d98d332ca3ffbbd522c3148f510fc1"])
        self.assertEqual(
            handle_opcode_stack(opcode, stack, index, asm_instruction_in_list),
            expectedOutput,
        )


if __name__ == "__main__":
    unittest.main()
