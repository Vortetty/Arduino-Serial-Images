#pragma GCC optimize("Ofast")
#include <Adafruit_GFX.h>    // Core graphics library
#include <Adafruit_TFTLCD.h> // Hardware-specific library

#define LCD_CS A3 // Chip Select goes to Analog 3
#define LCD_CD A2 // Command/Data goes to Analog 2
#define LCD_WR A1 // LCD Write goes to Analog 1
#define LCD_RD A0 // LCD Read goes to Analog 0
#define LCD_RESET A4 // Can alternately just connect to Arduino's reset pin
Adafruit_TFTLCD tft(LCD_CS, LCD_CD, LCD_WR, LCD_RD, LCD_RESET);

long pixelsNeeded = tft.width()*tft.height();
int t_width = tft.width();
int t_height = tft.height();

int i_width;
int i_height;

int width;
int height;

void setup() {
    Serial.begin(1152000*2);
    Serial.setTimeout(1);

    //while (!Serial.available());
    uint16_t identifier = tft.readID();
    tft.begin(identifier);
    tft.setRotation(3);
    t_width = tft.width();
    t_height = tft.height();
}

char s[2];
uint16_t c;
long long l = 0;

long offsetX, offsetY;

void loop() {
    //while (!Serial.available());
    byte tmp[4];
    Serial.write('0');
    while (!Serial.available());
    width = Serial.readString().toInt();
    Serial.write(i_width);
    Serial.write('0');
    while (!Serial.available());
    height = Serial.readString().toInt();
    Serial.write(i_height);

    offsetX = t_width/2 - width/2;
    offsetY = t_height/2 - height/2;

    //width = min(i_width, t_width);
    //height = min(i_height, t_height);
    tft.fillScreen(0);

    while (true) {
        Serial.write(32);
        while (Serial.available() < 63);
        
        for (long long i = 0; i < 32; i++){
            Serial.readBytes(s, 2);
            //memcpy(&c, s, sizeof(uint16_t));
            long x = abs(~(l % width)) + offsetX;
            long y = l / width + offsetY;
            tft.drawPixel(x, y, *(uint16_t*)(&s));
            l++;
        }
    }
}