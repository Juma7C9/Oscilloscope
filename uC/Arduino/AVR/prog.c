#include "prog.h"

#include <avr/io.h>
#include <avr/interrupt.h>
#include <util/atomic.h>
#include <util/setbaud.h>

volatile char timer1L, timer1H, resultL, resultH;

void uart_init(void) {
    UBRR0H = UBRRH_VALUE;
    UBRR0L = UBRRL_VALUE;

#if USE_2X
    UCSR0A |= _BV(U2X0);
#else
    UCSR0A &= ~(_BV(U2X0));
#endif

    UCSR0C = _BV(UCSZ01) | _BV(UCSZ00); /* 8-bit data */
    UCSR0B = _BV(RXEN0) | _BV(TXEN0);   /* Enable RX and TX */
}

void adc_init(void){
	ADMUX  = _BV(REFS0)|_BV(ADLAR);
	ADCSRA = _BV(ADEN)|_BV(ADSC)|_BV(ADATE)|_BV(ADIE)|_BV(ADPS2)|_BV(ADPS1);
#if ADC_FREE_RUNNING
	ADCSRB = 0;
#else 
	ADCSRB = _BV(ADTS1)|_BV(ADTS0); /* Prescaler CLK/64 */
#endif
}

void timers_init(void){
	TCCR1B = _BV(CS11)|_BV(CS10); 	 /* Prescaler CLK/64 */
	TCCR0A = _BV(WGM01);		 /* CTC mode: reset counter0 on compare match */
	TCCR0B = _BV(CS01)|_BV(CS00);	 /* Prescaler CLK/64 */
	OCR0A  = 15; 			 /* Reset timer0 at 15 */
}

void uart_putchar(char c) {
    loop_until_bit_is_set(UCSR0A, UDRE0); /* Wait until data register empty. */
    UDR0 = c;
}

ISR(ADC_vect) {
	timer1L = TCNT1L;	/* read timer1 low byte */
	timer1H = TCNT1H;	/* read timer1 high byte */

	resultL = ADCL;		/* Conversion result low byte */
	resultH = ADCH;		/* Conversion result high byte */

	TIFR0 = _BV(OCF0A); 	/* Clear interrupt flag */
}

int main(void){
	char valueL, valueH, timeL, timeH, chk;
	union {
		char field;
		struct {
			char checksum: 	4;
			char isTime: 	1;
			char isTrigger: 1;
			char valueL:	2;
		} s;
	} f;
	
	uart_init();
	adc_init();
	timers_init();
	sei();	

	f.field = 0;
	while( 1 ){
		ATOMIC_BLOCK( ATOMIC_RESTORESTATE ) { // Prevents data modification by interrupts
			valueL = resultL;				  //+see http://www.nongnu.org/avr-libc/user-manual/group__util__atomic.html
			valueH = resultH;				  //+
			timeL = timer1L;				  //+
			timeH = timer1H;				  //+
		}
		f.s.valueL = (resultL >> 6);
		chk = timeL ^ timeH ^ valueH;		// checksum (4-bit XOR) compute
		chk ^= ((f.field>>4) ^ (chk>>4));	// +
		f.s.checksum = 0b00001111 & chk;		// +

		uart_putchar( timeH );		//	|   highTime     |
		uart_putchar( timeL );		//+ |    lowTime     |
		uart_putchar( valueH );		//+ |   valueHigh    |
		uart_putchar( f.field );	//+ | vL |1|2|  chk  |
	}	
	return 0;
}	
