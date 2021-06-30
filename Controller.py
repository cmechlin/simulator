from collections import defaultdict
from Eprom import Eprom
from Instruction import Instruction


class Controller:
    def __init__(self):
        self.statuses = []
        self.eprom = None

        # program counter stores current execution point
        self.pc = 0

        self.running = False

        # Get Op Codes Classes
        self.instruction_mapping = defaultdict()
        for instructionClass in Instruction.__subclasses__():
            self.instruction_mapping[instructionClass.id_bytes] = instructionClass

    def run(self, eprom:Eprom):
        # load eprom
        self.eprom = eprom
        
        # do we need to advance pc after the header?

        # run program
        self.running = True
        while self.running:
            # get id byte at current program counter
            # to identify next op code
            id_bytes = self.eprom.get_word(self.pc)
            # decode instruction
            InstructionClass = self.instruction_mapping.get(id_bytes, None)
            if InstructionClass is None:
                raise Exception("Instruction not found")

            # we have a good instruction class
            instruction = InstructionClass()
            instruction.execute()

            self.pc += instruction.length



    # def process_instruction(self, instruction: Instruction):
    #     instruction.process()

    #     for byte in list(instructions):
    #         instruction = JIF_Instruction(byte)
    #         self.process_instruction(instruction)

    # def process_instructions(self,):
    #     pass

    # self.process_instructions(list(instructions))