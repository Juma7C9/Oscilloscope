#ifndef PROG_H
#define PROG_H
#endif

#define F_CPU 16000000UL
#define BAUD 500000
#define USE_2X 0
#define ADC_FREE_RUNNING 0

void uart_init(void);
void adc_init(void);
void timers_init(void);
void uart_putchar(char);

