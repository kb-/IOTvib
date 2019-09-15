//Read ADXL345 accelerometer data at 3200 Hz, send unscaled data in Serial binary packets
//ok, no data lost

#define F_CPU (48000000UL)
#define READ_F_HZ (800)
#define WAIT_TC16_REGS_SYNC(x) while(x->COUNT16.STATUS.bit.SYNCBUSY);
#define bufferSize 128

uint32_t t = 0;
uint32_t t1 = 0;
uint32_t oldcnt = 0;




//data
typedef __attribute__ ((aligned(4))) struct {
  uint32_t t;
  uint32_t cnt;
  int16_t x;
  int16_t y;
  int16_t z;
  uint16_t info;
} data_t;

char buf[bufferSize]={0};
data_t data;
int32_t len = 0;
int32_t pktSize=sizeof(data_t)+1; //packet lenght is size of data plus sync byte and size byte
//TO DO: should be sizeof(data_t)+2, fix other pktSize usues in code to not break it


double i = 0;



//Add the SPI library so we can communicate with the ADXL345 sensor
#include <SPI.h>

#define XGAIN (0.00376390)// 4mg per lsb
#define YGAIN (0.00376009)
#define ZGAIN (0.00349265)
#define ADXL345_REG_DATA_FORMAT         (0x31)    // Data format control

//https://www.sparkfun.com/tutorials/240
//http://forum.arduino.cc/index.php/topic,159313.0.html

//Assign the Chip Select signal to pin 10.
int CS=10;

//This is a list of some of the registers available on the ADXL345.
//To learn more about these and the rest of the registers on the ADXL345, read the datasheet!
char POWER_CTL = 0x2D;  //Power Control Register
char DATA_FORMAT = 0x31;
char DATAX0 = 0x32; //X-Axis Data 0
char DATAX1 = 0x33; //X-Axis Data 1
char DATAY0 = 0x34; //Y-Axis Data 0
char DATAY1 = 0x35; //Y-Axis Data 1
char DATAZ0 = 0x36; //Z-Axis Data 0
char DATAZ1 = 0x37; //Z-Axis Data 1

char BW_RATE = 0x2C;    //Data rate register
char DATARATE_3200_HZ    = 0b1111;

//This buffer will hold values read from the ADXL345 registers.
unsigned char values[10];
//These variables will be used to hold the x,y and z axis accelerometer values.
uint16_t x,y,z;


void setup() {
  //Initiate an SPI communication instance.
  SPI.begin();
  //Configure the SPI connection for the ADXL345.
  SPI.setDataMode(SPI_MODE3);
  
  while (!SerialUSB) {
  ; // wait for SerialUSB port to connect.
  }
  SerialUSB.begin(250000);
  setupTCInterrupts();
  enableTCInterrupts();
//  SysTick->LOAD = 15000UL;//reset SysTick at 3200 Hz (clock/3200) for accuracy testing


  //Set up the Chip Select pin to be an output from the Arduino.
  pinMode(CS, OUTPUT);
  //Before communication starts, the Chip Select pin needs to be set high.
  digitalWrite(CS, HIGH);

  /* Read the data format register to preserve bits */
  //(char registerAddress, int numBytes, unsigned char * values)
  unsigned char format;
  readRegister(ADXL345_REG_DATA_FORMAT,1,&format);
   /* Update the data rate */
  format &= ~0x0F;
  //Put the ADXL345 into +/- 16G range by writing the value 0x01 to the DATA_FORMAT register. 0b11
  unsigned char range = 0b11;
  format |= range;
  /* Make sure that the FULL-RES bit is enabled for range scaling */
  format |= 0x08;
  
  writeRegister(DATA_FORMAT, format);
  //Put the ADXL345 into Measurement Mode by writing 0x08 to the POWER_CTL register.
  writeRegister(POWER_CTL, 0x08);  //Measurement mode 
  //set datarate to 3200 Hz
  writeRegister(BW_RATE, DATARATE_3200_HZ);
}

void loop() {
  //Create a SerialUSB connection to display the data on the terminal.
  if(len>(bufferSize-pktSize)){
    SerialUSB.write(buf,len);
    len = 0;
    buf[bufferSize]={0};
  }
}



volatile bool TC5_ISR_Enabled=false;

void setupTCInterrupts() {

  // Enable GCLK for TC4 and TC5 (timer counter input clock)
  GCLK->CLKCTRL.reg = (uint16_t) (GCLK_CLKCTRL_CLKEN | GCLK_CLKCTRL_GEN_GCLK0 | GCLK_CLKCTRL_ID(GCM_TC4_TC5));
  while (GCLK->STATUS.bit.SYNCBUSY);

  TC5->COUNT16.CTRLA.reg &= ~TC_CTRLA_ENABLE;   // Disable TCx
  WAIT_TC16_REGS_SYNC(TC5)                      // wait for sync

  TC5->COUNT16.CTRLA.reg |= TC_CTRLA_MODE_COUNT16;   // Set Timer counter Mode to 16 bits
  WAIT_TC16_REGS_SYNC(TC5)

  TC5->COUNT16.CTRLA.reg |= TC_CTRLA_WAVEGEN_MFRQ; // Set TC as normal Normal Frq
  WAIT_TC16_REGS_SYNC(TC5)

  TC5->COUNT16.CTRLA.reg |= TC_CTRLA_PRESCALER_DIV1;   // Set perscaler
  WAIT_TC16_REGS_SYNC(TC5)


  TC5->COUNT16.CC[0].reg = F_CPU/READ_F_HZ;
  WAIT_TC16_REGS_SYNC(TC5)


  TC5->COUNT16.INTENSET.reg = 0;              // disable all interrupts
  TC5->COUNT16.INTENSET.bit.OVF = 1;          // enable overfollow
//    TC5->COUNT16.INTENSET.bit.MC0 = 1;         // enable compare match to CC0


  //set a higher priority for TC5 than SERCOM3 (priority to counter over SerialUSB)
  //NVIC_DisableIRQ(SERCOM3_IRQn);
  NVIC_SetPriority(SERCOM3_IRQn, 1);
//  //NVIC_EnableIRQ(SERCOM3_IRQn);
  NVIC_SetPriority(TC5_IRQn, 0);


  // Enable InterruptVector
  NVIC_EnableIRQ(TC5_IRQn);


  // Enable TC
  TC5->COUNT16.CTRLA.reg |= TC_CTRLA_ENABLE;
  WAIT_TC16_REGS_SYNC(TC5)

}

static void enableTCInterrupts() {

  TC5_ISR_Enabled=true;
  NVIC_EnableIRQ(TC5_IRQn);
  TC5->COUNT16.INTENSET.bit.OVF = 1;
  //  TC5->COUNT16.CTRLA.reg |= TC_CTRLA_ENABLE;    //Enable TC5
  //  WAIT_TC16_REGS_SYNC(TC5)                      //wait for sync
}

static void disableTCInterrupts() {

  TC5_ISR_Enabled=false;
  //NVIC_DisableIRQ(TC5_IRQn);
  TC5->COUNT16.INTENCLR.bit.OVF = 1;
}


void TC5_Handler(){
  
  if (TC5->COUNT16.INTFLAG.bit.OVF == 1)
  {
    //READ CODE
   // __disable_irq();
    //__enable_irq();
    if(len<=(bufferSize-pktSize)){
//      __disable_irq();
      i+=1;
      t = micros();
      data.t = t;
      data.cnt = i;   
      readRegister(DATAX0, 6, values);  
//      data.cnt = SysTick->VAL+7500;//accuracy testing (unit=clock cycle, contant = perfect accuracy)
      //The ADXL345 gives 13-bit acceleration values, but they are stored as bytes (8-bits). To get the full value, two bytes must be combined for each axis.
      data.x = ((int)values[1]<<8)|(int)values[0];//The X value is stored in values[0] and values[1].
      data.y = ((int)values[3]<<8)|(int)values[2];//The Y value is stored in values[2] and values[3].
      data.z = ((int)values[5]<<8)|(int)values[4];//The Z value is stored in values[4] and values[5].
      memcpy(&buf[len],&data,sizeof(data_t));
      len+=sizeof(data_t);
      buf[len]=0XAA; //sync
      len++;
      buf[len]=sizeof(data_t); //data len
      len++;
//      t1 = micros();
//      __enable_irq();
    }
    //READ CODE
    TC5->COUNT16.INTFLAG.bit.OVF = 1;    // writing a one clears the flag ovf flag
  }
}


void writeRegister(char registerAddress, char value){
  //Set Chip Select pin low to signal the beginning of an SPI packet.
  digitalWrite(CS, LOW);
  //Transfer the register address over SPI.
  SPI.transfer(registerAddress);
  //Transfer the desired register value over SPI.
  SPI.transfer(value);
  //Set the Chip Select pin high to signal the end of an SPI packet.
  digitalWrite(CS, HIGH);
}

//This function will read a certain number of registers starting from a specified address and store their values in a buffer.
//Parameters:
//  char registerAddress - The register addresse to start the read sequence from.
//  int numBytes - The number of registers that should be read.
//  char * values - A pointer to a buffer where the results of the operation should be stored.
void readRegister(char registerAddress, int numBytes, unsigned char * values){
  //Since we're performing a read operation, the most significant bit of the register address should be set.
  char address = 0x80 | registerAddress;
  //If we're doing a multi-byte read, bit 6 needs to be set as well.
  if(numBytes > 1)address = address | 0x40;
 
  //Set the Chip select pin low to start an SPI packet.
  digitalWrite(CS, LOW);
  //Transfer the starting register address that needs to be read.
  SPI.transfer(address);
  //Continue to read registers until we've read the number specified, storing the results to the input buffer.
  for(int i=0; i<numBytes; i++){
    values[i] = SPI.transfer(0x00);
  }
  //Set the Chips Select pin high to end the SPI packet.
  digitalWrite(CS, HIGH);
}
