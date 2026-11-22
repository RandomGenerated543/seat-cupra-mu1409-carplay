ENTRY(auxiliary_layout)
SECTIONS { . = 0x1504a0; .payload : { KEEP(*(.entry)) KEEP(*(.url_entry)) *(.text .text.*) *(.rodata .rodata.*) } /DISCARD/ : { *(.ARM.exidx*) *(.ARM.extab*) *(.comment) *(.note.GNU-stack) } }
fopen = 0xefb30;
fclose = 0xefb50;
fread = 0xefb40;
fprintf = 0xefc30;
dlsym = 0xf0230;
snprintf = 0xefa10;
sscanf = 0xef9e0;
memcmp = 0xef900;
memchr = 0xf0100;
__get_errno_ptr = 0xef9b0;
