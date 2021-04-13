(Istore_name,  # 0
    Iload_const,  # 1
    Iadd,  # 2
    Imult,  # 3
    Idiv,  # 4
    Isub,  # 5
    Inop,  # 6
    Irem,  # 7
    Ipow,  # 8
    BR,  # 9
    BRT,  # 10
    BRF,  # 11
    ICONST,  # 12
    LOAD,  # 13
    GLOAD,  # 14
    Istop #15
    )=range(16)

HAVE_ARGUMENT=0 # up to this bytecode, opcodes have argument 
WE_LOAD_CONSTS=1
