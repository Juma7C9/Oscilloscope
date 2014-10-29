#include "avr/io.h"
#include "avr/interrupt.h"
#include "util/atomic.h"

volatile byte timer1L, timer1H;
volatile byte resultL, resultH;

ISR(ADC_vect) {
		timer1L = TCNT1L;	// read timer1 low byte
		timer1H = TCNT1H;	// read timer1 high byte
	
		resultL = ADCL;		// Conversion result low byte
		resultH = ADCH;		// Conversion result high byte
}

void setup()
{
	TCCR1A = B00000000; // Select timer1 "default" mode 
	TCCR1B = B00000011; //+(see http://www.atmel.com/Images/doc8161.pdf page 134)
	TCCR1C = B00000000; //+
	TIMSK1 = B00000000; //+
	TIFR1  = B00000000; //+
	
	ADMUX  = B01100000; // ADC Setting (page 262)
	ADCSRA = B11101110; //+
	ADCSRB = B00000000; //+
	
	//delay(5000);
	
	Serial.begin(1000000); // 1Mbps
	Serial.write( 0 );
	Serial.write( 0 );
	Serial.write( 0 );
	Serial.write( 0 );
	Serial.write( 0 );
	Serial.write( 0 );
	Serial.write( 0 );
	Serial.write( 0 );
}

void loop()
{
	byte valueL, valueH, timeL, timeH, chk;
	union {
		byte field;
		struct {
			byte checksum: 	4;
			byte isTime: 	1;
			byte isTrigger: 1;
			byte valueL:	2;
		} s;
	} f;
	
	f.field = 0;
	
	while( true ){
		ATOMIC_BLOCK( ATOMIC_RESTORESTATE ) { // Prevents data modification by interrupts
			valueL = resultL;				  //+see http://www.nongnu.org/avr-libc/user-manual/group__util__atomic.html
			valueH = resultH;				  //+
			timeL = timer1L;				  //+
			timeH = timer1H;				  //+
		}
		f.s.valueL = (resultL >> 6);
		chk = timeL ^ timeH ^ valueH;		// checksum (4-bit XOR) compute
		chk ^= ((f.field>>4) ^ (chk>>4));	// +
		f.s.checksum = B00001111 & chk;		// +

		Serial.write( timeH );		//	|   highTime     |
		Serial.write( timeL );		//+ |    lowTime     |
		Serial.write( valueH );		//+ |   valueHigh    |
		Serial.write( f.field );	//+ | vL |1|2|  chk  |
	}
}
