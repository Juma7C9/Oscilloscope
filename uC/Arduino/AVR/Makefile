PROG=prog.c
PROC=atmega328p
PORT=/dev/ttyACM0

CC=avr-gcc
CFLAGS=-mmcu=$(PROC)


help:
	@echo 'Help details:'
	@echo 'hex: compile hex file'
	@echo 'flash: install hex file'
	@echo 'program: compile hex and install'

hex:
	$(CC) $(CFLAGS) -o prog.elf $(PROG)
	avr-objcopy -O ihex prog.elf prog.hex
	-rm prog.elf

flash:
	avrdude -c arduino -p $(PROC) -P $(PORT) -U flash:w:prog.hex

program: hex flash
