# Copyright 2019 - Omar Sandoval
# SPDX-License-Identifier: GPL-3.0+

# This script generates "arch_foo.c" from "arch_foo.c.in". It uses
# "parse_arch.awk" to parse the input file and generates three definitions:
#
# 1. An array of register definitions:
#    static const struct drgn_register registers[];
#
# 2. A lookup function (implemented as a trie using nested switch statements):
#    static const struct drgn_register *register_by_name(const char *name);
#
# 3. A macro containing initializers for the "name", "arch", "registers",
#    "num_registers", and "register_by_name" members of "struct
#    drgn_architecture_info":
#    #define ARCHITECTURE_INFO
#
# The prologue and epilogue are copied before and after these definitions,
# respectively.

function add_to_trie(node, s, value,     char) {
	if (length(s) == 0) {
		node[""] = value
	} else {
		char = substr(s, 1, 1)
		if (!(char in node)) {
			# Force node[char] to be an array.
			node[char][""] = ""
			delete node[char][""]
		}
		add_to_trie(node[char], substr(s, 2), value)
	}
}

function trie_to_switch(node, indent,     char) {
	print indent "switch (*(p++)) {"
	PROCINFO["sorted_in"] = "@ind_str_asc"
	for (char in node) {
		if (length(char) == 0) {
			print indent "case '\\0':"
			print indent "\treturn &registers[" node[""] "];"
		} else {
			print indent "case '" char "':"
			trie_to_switch(node[char], "\t" indent)
		}
	}
	print indent "default:"
	print indent "\treturn NULL;"
	print indent "}"
}

ENDFILE {
	print "/* Generated by libdrgn/build-aux/gen_arch.awk. */"

	if (length(prologue) != 0)
		print prologue

	print "static const struct drgn_register registers[] = {"
	i = 0
	split("", trie)
	PROCINFO["sorted_in"] = "@val_num_asc"
	for (reg in registers) {
		print "\t{ \"" reg "\", " registers[reg] ", },"
		add_to_trie(trie, reg, i++)
	}
	print "};"
	print ""

	print "static const struct drgn_register *register_by_name(const char *p)"
	print "{"
	trie_to_switch(trie, "\t")
	print "}"
	print ""

	print "#define ARCHITECTURE_INFO \\"
	print "\t.name = \"" arch_name "\", \\"
	print "\t.arch = DRGN_ARCH_" toupper(sanitize(arch_name)) ", \\"
	print "\t.registers = registers, \\"
	print "\t.num_registers = " i ", \\"
	print "\t.register_by_name = register_by_name"

	printf "%s", epilogue
}
