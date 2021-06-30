"""
  Using olefile library

  olefile (formerly OleFileIO_PL) is copyright (c) 2005-2020 Philippe Lagadec (http://www.decalage.info)

All rights reserved.

https://olefile.readthedocs.io/en/latest/Howto.html
"""
import olefile

"""
  CCF, VEQ and NEQ are all OLE files
  NCF is not. looks proprietary

  Equation Storage: "Equations"
  Order Storage Name: "Orders"
  Print Order Stream: "Print"
  Compile Order Stream: "Compile"
  Equation Directory Name: "$DIR$"

  const BYTE JIT_INSTR = 254;   FE
  const BYTE JIF_INSTR = 253;   FD
  const BYTE JMP_INSTR = 251;   FB
  const BYTE FALSE_EXIT = 248;  F8
  const BYTE TRUE_EXIT = 247;   F7
  const BYTE BREAK = 244;       F4
  const BYTE NEXT_EQ = 242;     F2

  const int MAX_WIRES_PER_EQUATION = 30;
  const int MAX_STATUS_PER_WIRE = 50;
  const int MAX_STATUSES_PER_EQ = MAX_STATUS_PER_WIRE * MAX_WIRES_PER_EQUATION;

  const int NV_MAX_WIRES_PER_EQUATION = 10;
  const int NV_MAX_STATUS_PER_WIRE = 25;
  const int NV_MAX_STATUSES_PER_EQ = NV_MAX_STATUS_PER_WIRE * NV_MAX_WIRES_PER_EQUATION;

  const CString MAX_STATUS_NAME = "            ";
  const BYTE CHARS_PER_ROW = 3;

  meta.num_words is used for file version

  to load equations
  check version
  enter equation storage
  open directory stream
  check if empty
  read crc, double word 32-bits. This is a CRC-31 for vital
  while still bytes
  read equation name. longest equation name 12, longest valid stream name 32
  name of equations are property streams, which begin with 0x05 according to spec

  Load equation stream
  read equation connections
    read connection (word)
    connectionlist size = conn +2
    graphiclist size = conn + 2
    for each row of connection list to connlist size
      read source chartovbbool
      read statusname string
      read operation. size?
      read resname string
      read negation chartovbbool
      read connectioncount size?
      for each conn to connection count

  Equation Stream
  -----------------
  equation connections
    number of connections (upper bound - 1) int
    for each connection record
      write source (T/F)
      0x0A + write status name string
      write operation (type?)
      write resname string
      write negation (T/F)
      write connection count (type?)
      for each connection in connection count
        write connection (type?)



  timer data
    timer default value
    timer min value
    timer max value if version > 1
    timer enable string
    timer complete string
  equation crc
    32bit crc31 of equation
  graphic data
    T or F (including source) that is energized or deenergized state
  notes
    int charactercount (32bits) note string
  save

  read timer data
  read equation crc

  Properties from CCF
  railroad = title
  area subdivision = template
  location name address = subject
  designer = author
  comments = comments
  file major version = wordcount
  file minor version = charactercount

  chassis stream
  read file version


"""

#
#
#

def main():
    filepath = ".\\simpleapp.veq"
    # with open(filepath, "rb") as f:
    isOle = olefile.isOleFile(filepath)
    assert isOle
    print(f"File is OLE File: {isOle}")

    with olefile.OleFileIO(filepath, raise_defects=olefile.DEFECT_INCORRECT) as ole:
        print("Non-fatal issues raised during parsing:")
        if ole.parsing_issues:
            for exctype, msg in ole.parsing_issues:
                print("- %s: %s" % (exctype.__name__, msg))
        else:
            print("None")
        
        meta = ole.get_metadata()
        print(f"Number of Characters: {meta.num_chars}")
        print(meta.dump())
        print(ole.listdir())
        print(ole.listdir(streams=True, storages=False))
        print(ole.listdir(streams=False, storages=True))

        if ole.exists("equations"):
          print("Equations are here")
          if(ole.exists("equations/$dir$")):
            print("equation dir exists")
            # open ole stream
            equdir = ole.openstream("equations/$dir$")
            data = equdir.read()
            print(data)

        # Open Stream
        # Read Equation Connections
        # Read Timer Data
        # if filever <= 1
        #   Read Recorder Data
        # else
        #   include recorder info in crc calc
        #   if product family config IXS VPM-3
        #     


if __name__ == "__main__":
    main()
