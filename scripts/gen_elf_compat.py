#!/usr/bin/env python3
# Copyright (c) Meta Platforms, Inc. and affiliates.
# SPDX-License-Identifier: LGPL-2.1-or-later

import argparse
import re
import subprocess

# Macros missing from glibc 2.17, which is the oldest version we test against
# (when we build manylinux2014 wheels).
MACROS = (
    # Added in glibc 2.18.
    "NT_FILE",
    # Added in glibc 2.24.
    "EM_RISCV",
    # Added in glibc 2.27.
    # We don't need all of the RISC-V relocation types, but it doesn't hurt.
    "R_RISCV_NONE",
    "R_RISCV_32",
    "R_RISCV_64",
    "R_RISCV_RELATIVE",
    "R_RISCV_COPY",
    "R_RISCV_JUMP_SLOT",
    "R_RISCV_TLS_DTPMOD32",
    "R_RISCV_TLS_DTPMOD64",
    "R_RISCV_TLS_DTPREL32",
    "R_RISCV_TLS_DTPREL64",
    "R_RISCV_TLS_TPREL32",
    "R_RISCV_TLS_TPREL64",
    # Added in glibc 2.28.
    "R_RISCV_BRANCH",
    "R_RISCV_JAL",
    "R_RISCV_CALL",
    "R_RISCV_CALL_PLT",
    "R_RISCV_GOT_HI20",
    "R_RISCV_TLS_GOT_HI20",
    "R_RISCV_TLS_GD_HI20",
    "R_RISCV_PCREL_HI20",
    "R_RISCV_PCREL_LO12_I",
    "R_RISCV_PCREL_LO12_S",
    "R_RISCV_HI20",
    "R_RISCV_LO12_I",
    "R_RISCV_LO12_S",
    "R_RISCV_TPREL_HI20",
    "R_RISCV_TPREL_LO12_I",
    "R_RISCV_TPREL_LO12_S",
    "R_RISCV_TPREL_ADD",
    "R_RISCV_ADD8",
    "R_RISCV_ADD16",
    "R_RISCV_ADD32",
    "R_RISCV_ADD64",
    "R_RISCV_SUB8",
    "R_RISCV_SUB16",
    "R_RISCV_SUB32",
    "R_RISCV_SUB64",
    "R_RISCV_GNU_VTINHERIT",
    "R_RISCV_GNU_VTENTRY",
    "R_RISCV_ALIGN",
    "R_RISCV_RVC_BRANCH",
    "R_RISCV_RVC_JUMP",
    "R_RISCV_RVC_LUI",
    "R_RISCV_GPREL_I",
    "R_RISCV_GPREL_S",
    "R_RISCV_TPREL_I",
    "R_RISCV_TPREL_S",
    "R_RISCV_RELAX",
    "R_RISCV_SUB6",
    "R_RISCV_SET6",
    "R_RISCV_SET8",
    "R_RISCV_SET16",
    "R_RISCV_SET32",
    "R_RISCV_32_PCREL",
    # Added in glibc 2.30.
    "NT_ARM_PAC_MASK",
)


def main() -> None:
    argparse.ArgumentParser(
        description="Generate definitions missing from older versions of glibc for libdrgn/include/elf.h from elf.h"
    ).parse_args()

    contents = subprocess.check_output(
        ["gcc", "-dD", "-E", "-"],
        input="#include <elf.h>\n",
        universal_newlines=True,
    )

    macros = {
        match.group(1): match.group(2)
        for match in re.finditer(
            r"^\s*#\s*define\s+(" + "|".join(MACROS) + r")\s+(.*)",
            contents,
            re.MULTILINE,
        )
    }

    print("// Generated by scripts/gen_elf_compat.py.")
    for macro in MACROS:
        print("#ifndef", macro)
        print("#define", macro, macros[macro])
        print("#endif")


if __name__ == "__main__":
    main()
