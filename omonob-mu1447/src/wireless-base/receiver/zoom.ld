ENTRY(auxiliary_zoom)
SECTIONS { . = 0x1504a0; .payload : { KEEP(*(.entry)) *(.text .text.*) *(.rodata .rodata.*) } /DISCARD/ : { *(.ARM.exidx*) *(.ARM.extab*) *(.comment) *(.note.GNU-stack) } }
