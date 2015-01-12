/*Copyright (c) 2015, NC Thompson
All rights reserved.
Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:

1) Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.

2) Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.

3) Neither the name of the ORGANIZATION nor the names of its contributors may be used to endorse or promote products derived from this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
*/

#include "U8glib.h"

U8GLIB_ST7920_128X64_1X u8g(13, 11, 10);	// SPI Com: SCK = en = 13, MOSI = rw = 11, CS = di = 10



const uint8_t bat_full_bitmap[] U8G_PROGMEM = {
  0x00,         // 00000000
  0X66,         // 01100110
  0xFF,         // 11111111
  0xFF,         // 11111111
  0xFF,         // 11111111
  0xFF,         // 11111111
  0xFF,         // 11111111
  0x00          // 00000000
};

const uint8_t bat_half_bitmap[] U8G_PROGMEM = {
  0x00,         // 00000000
  0X66,         // 01100110
  0xFF,         // 11111111
  0x81,         // 10000001
  0xFF,         // 11111111
  0xFF,         // 11111111
  0xFF,         // 11111111
  0x00          // 00000000
};

const uint8_t bat_low_bitmap[] U8G_PROGMEM = {
  0x00,         // 00000000
  0X66,         // 01100110
  0xFF,         // 11111111
  0x81,         // 10000001
  0x81,         // 10000001
  0xFF,         // 11111111
  0xFF,         // 11111111
  0x00          // 00000000
};

const uint8_t bat_empty_bitmap[] U8G_PROGMEM = {
  0x00,         // 00000000
  0X66,         // 01100110
  0xFF,         // 11111111
  0x81,         // 10000001
  0x81,         // 10000001
  0x81,         // 10000001
  0xFF,         // 11111111
  0x00          // 00000000
};

const uint8_t face[] U8G_PROGMEM = {
  0X18,         // 00011000
  0x24,         // 00100100
  0x42,         // 01000010
  0xA5,         // 10100101
  0x81,         // 10000001
  0x5A,         // 01011010
  0x24,         // 00100100
  0x18          // 00011000
};

const uint8_t lightning[] U8G_PROGMEM = {
  0X1F,         // 00011111
  0x3E,         // 00111110
  0x7C,         // 01111000
  0xFF,         // 11111111
  0x1C,         // 00011100
  0x30,         // 00110000
  0x60,         // 01100000
  0x80          // 10000000
};

const uint8_t light_off[] U8G_PROGMEM = {
  0X18,         // 00011000
  0x24,         // 00100100
  0x42,         // 01000010
  0x42,         // 01000010
  0x24,         // 00100100
  0x24,         // 00100100
  0x18,         // 00011000
  0x18,         // 00011000
};

const uint8_t light_on[] U8G_PROGMEM = {
  0X5A,         // 01011010
  0xA5,         // 10100101
  0x42,         // 01000010
  0x42,         // 01000010
  0x66,         // 01100110
  0xA5,         // 10100101
  0x18,         // 00011000
  0x18,         // 00011000
};

const uint8_t temperature[] U8G_PROGMEM = {
  0b00011000,         // 00111100
  0b00011110,         // 00100100
  0b00011000,         // 00111100
  0b00011110,         // 00111100
  0b00011000,         // 01111110
  0b00111100,         // 01111110
  0b00111100,         // 00111100
  0b00011000,         // 00011000
};

String goodBuf = "=09 26 16 Jan 2015222513.34 50.62232.41.62234.21.5150.151.0=";
char readBuf[61] = "=09 26 16 Jan 2015222513.34 50.62232.41.62234.21.5150.151.0=";
char time[18] = "14 45 16 Jan 2015";

char batV[6] = "14.00";
char batA[7] = "-24.36";

char inV[6] = "230.0";
char inA[5] = "0.90";
char inF[5] = "50.0";

char outV[6] = "231.0";
char outA[5] = "0.99";
char outF[5] = "50.1";

char bitMaps[5] = "1114";

char charBuf = 0;
char sum = 0;
char count = 0;

boolean reading = false;

boolean blnk = true;
uint8_t charge = 0;


// U8GLIB draw procedure: output the screen
void updateValues(void) {
 //update time
 goodBuf.substring(1,18).toCharArray(time, 18);
 
 goodBuf.substring(18,22).toCharArray(bitMaps, 5);

 goodBuf.substring(22,27).toCharArray(batV, 6); 
 goodBuf.substring(27,33).toCharArray(batA, 7);

 goodBuf.substring(33,38).toCharArray(inV, 6); 
 goodBuf.substring(38,42).toCharArray(inA, 5);

 goodBuf.substring(42,47).toCharArray(outV, 6); 
 goodBuf.substring(47,51).toCharArray(outA, 5);

 goodBuf.substring(51,55).toCharArray(inF, 5); 
 goodBuf.substring(55,59).toCharArray(outF, 5); 
  
}

void draw(void) {
  drawHeader();
  drawUnits();
  drawInfo();
}

void drawInfo(void) {

  u8g.setFont(u8g_font_6x13);
  
  u8g.drawStr(8, 35, batV);
  u8g.drawStr(2, 46, batA);
  
  u8g.drawStr(50, 35, inV);
  u8g.drawStr(56, 46, inA);
  
  
  u8g.drawStr(90, 35, outV);
  u8g.drawStr(96, 46, outA);
  
  u8g.setFont(u8g_font_5x8);
  u8g.drawStr(56, 55, inF);
  u8g.drawStr(96, 55, outF);
  
  //u8g.drawBitmapP( 50, 47, 1, 8, face);
  //u8g.drawBitmapP( 80, 47, 1, 8, light_on);
}

void drawUnits(void) {
  u8g.setFont(u8g_font_6x13B);
  u8g.drawStr(2, 22, "Battery");
  u8g.drawStr(50, 22, "In");
  u8g.drawStr(90, 22, "Out");
  
  u8g.drawStr(38, 35, "V");
  u8g.drawStr(38, 46, "A");
  
  u8g.drawStr(80, 35, "V");
  u8g.drawStr(80, 46, "A");
  
  
  u8g.drawStr(120, 35, "V");
  u8g.drawStr(120, 46, "A");
  
  u8g.setFont(u8g_font_5x8);
  u8g.drawStr(76, 55, "Hz");
  u8g.drawStr(116, 55, "Hz");
}

void drawHeader(void) {
  u8g.drawHLine(0, 10, 128);
  u8g.drawHLine(0, 11, 128);
  
  if (bitMaps[0] == '1') {
    u8g.drawBitmapP( 88, 1, 1, 8, temperature);
  }
  else if (bitMaps[0] == '2' && blnk == true) {
    u8g.drawBitmapP( 88, 1, 1, 8, temperature);
  }
  
  if (bitMaps[1] == '1') {
    u8g.drawBitmapP( 98, 1, 1, 8, light_off);
  }
  else if (bitMaps[1] == '2' && blnk == true) {
    u8g.drawBitmapP( 98, 1, 1, 8, light_off);
  }
  
  if (bitMaps[2] == '1') {
    u8g.drawBitmapP( 108, 1, 1, 8, lightning);
  }
  else if (bitMaps[2] == '2' && blnk == true) {
    u8g.drawBitmapP( 108, 1, 1, 8, lightning);
  }
  
  switch (bitMaps[3]) {
    
    
   case '0':
     u8g.drawBitmapP( 118, 1, 1, 8, bat_full_bitmap);
     break;
   
   case '1':
     u8g.drawBitmapP( 118, 1, 1, 8, bat_half_bitmap);
     break;
     
   case '2':
     u8g.drawBitmapP( 118, 1, 1, 8, bat_low_bitmap);
     break;
   
   case '3':
     if (blnk == true) {
       u8g.drawBitmapP( 118, 1, 1, 8, bat_empty_bitmap);
     }
     break;
     
  case '4':
     if (blnk == true) {
       u8g.drawBitmapP( 118, 1, 1, 8, bat_full_bitmap);
     }
     break;
    
  case '5': 
    switch (charge){
      case 0:
      u8g.drawBitmapP( 118, 1, 1, 8, bat_empty_bitmap);
      break;
      
      case 1:
      u8g.drawBitmapP( 118, 1, 1, 8, bat_low_bitmap);
      break;
      
      case 2:
      u8g.drawBitmapP( 118, 1, 1, 8, bat_half_bitmap);
      break;
      
      case 3:
      u8g.drawBitmapP( 118, 1, 1, 8, bat_full_bitmap);
      break;
    }
   break;
  
  }
  
  
  u8g.setFont(u8g_font_5x8);
  u8g.drawStr(2, 8, time);
  
  if (blnk == true) {
    u8g.drawStr(12, 8, ":");
  }
}

// Arduino master setup
void setup(void) {
  // set font for the console window
  //u8g.setFont(u8g_font_5x7);
  
  
  // set upper left position for the string draw procedure
  u8g.setFontPosTop();
  
    // assign default color value
  if ( u8g.getMode() == U8G_MODE_R3G3B2 ) 
    u8g.setColorIndex(255);     // white
  else if ( u8g.getMode() == U8G_MODE_GRAY2BIT )
    u8g.setColorIndex(3);         // max intensity
  else if ( u8g.getMode() == U8G_MODE_BW )
    u8g.setColorIndex(1);         // pixel on

  
  delay(1000);                  // do some delay
  Serial.begin(9600);        // init serial

  
}

void loop(void) {

 if ( Serial.available()) {
   charBuf = Serial.read();
   
   if (charBuf == '=') {
     sum = charBuf;
     count = 0;
     reading = true;
  
   } else if (reading == true){
     sum += charBuf;
     count ++; 
     reading = true;
   }
   readBuf[count] = charBuf;
   
   if (count == 59) {
     if (sum == 0) {
       goodBuf = String(readBuf);
       updateValues();
     }
     reading = false;
   }
 }
 if (reading == false) {
     // picture loop
    u8g.firstPage();  
    do {
      draw();
    } while( u8g.nextPage() );
   delay(500); 
   charge = (charge + 1) %4;
   blnk = !blnk;
 }
}
