
#include "mbed.h"
#include "ssd1331.h"

#define countof(x) ( sizeof(x) / sizeof(x[0]) )

static const char font6x8[0x60][6] = {
    { 0x00,0x00,0x00,0x00,0x00,0x00 } , /*SPC */
    { 0x00,0x00,0x5F,0x00,0x00,0x00 } , /* !  */
    { 0x04,0x03,0x04,0x03,0x00,0x00 } , /* "  */
    { 0x28,0x7E,0x14,0x3F,0x0A,0x00 } , /* #  */
    { 0x24,0x2A,0x7F,0x2A,0x12,0x00 } , /* $  */
    { 0x23,0x13,0x08,0x64,0x62,0x00 } , /* %  */
    { 0x30,0x4E,0x59,0x26,0x50,0x00 } , /* &  */
    { 0x00,0x00,0x02,0x01,0x00,0x00 } , /* '  */
    { 0x00,0x00,0x1C,0x22,0x41,0x00 } , /* (  */
    { 0x41,0x22,0x1C,0x00,0x00,0x00 } , /* )  */
    { 0x22,0x14,0x08,0x14,0x22,0x00 } , /* *  */
    { 0x08,0x08,0x3E,0x08,0x08,0x00 } , /* +  */
    { 0x50,0x30,0x00,0x00,0x00,0x00 } , /* ,  */
    { 0x08,0x08,0x08,0x08,0x08,0x00 } , /* -  */
    { 0x60,0x60,0x00,0x00,0x00,0x00 } , /* .  */
    { 0x20,0x10,0x08,0x04,0x02,0x00 } , /* /  */
    { 0x3E,0x51,0x49,0x45,0x3E,0x00 } , /* 0  */
    { 0x00,0x42,0x7F,0x40,0x00,0x00 } , /* 1  */
    { 0x62,0x51,0x49,0x49,0x46,0x00 } , /* 2  */
    { 0x22,0x41,0x49,0x49,0x36,0x00 } , /* 3  */
    { 0x18,0x14,0x12,0x7F,0x10,0x00 } , /* 4  */
    { 0x2F,0x45,0x45,0x45,0x39,0x00 } , /* 5  */
    { 0x3E,0x49,0x49,0x49,0x32,0x00 } , /* 6  */
    { 0x01,0x61,0x19,0x05,0x03,0x00 } , /* 7  */
    { 0x36,0x49,0x49,0x49,0x36,0x00 } , /* 8  */
    { 0x26,0x49,0x49,0x49,0x3E,0x00 } , /* 9  */
    { 0x00,0x36,0x36,0x00,0x00,0x00 } , /* :  */
    { 0x00,0x56,0x36,0x00,0x00,0x00 } , /* ;  */
    { 0x00,0x08,0x14,0x22,0x41,0x00 } , /* <  */
    { 0x14,0x14,0x14,0x14,0x14,0x00 } , /* =  */
    { 0x41,0x22,0x14,0x08,0x00,0x00 } , /* >  */
    { 0x02,0x01,0x59,0x09,0x06,0x00 } , /* ?  */
    { 0x3E,0x41,0x5D,0x55,0x2E,0x00 } , /* @  */
    { 0x60,0x1C,0x13,0x1C,0x60,0x00 } , /* A  */
    { 0x7F,0x49,0x49,0x49,0x36,0x00 } , /* B  */
    { 0x3E,0x41,0x41,0x41,0x22,0x00 } , /* C  */
    { 0x7F,0x41,0x41,0x22,0x1C,0x00 } , /* D  */
    { 0x7F,0x49,0x49,0x49,0x41,0x00 } , /* E  */
    { 0x7F,0x09,0x09,0x09,0x01,0x00 } , /* F  */
    { 0x1C,0x22,0x41,0x49,0x3A,0x00 } , /* G  */
    { 0x7F,0x08,0x08,0x08,0x7F,0x00 } , /* H  */
    { 0x00,0x41,0x7F,0x41,0x00,0x00 } , /* I  */
    { 0x20,0x40,0x40,0x40,0x3F,0x00 } , /* J  */
    { 0x7F,0x08,0x14,0x22,0x41,0x00 } , /* K  */
    { 0x7F,0x40,0x40,0x40,0x00,0x00 } , /* L  */
    { 0x7F,0x04,0x18,0x04,0x7F,0x00 } , /* M  */
    { 0x7F,0x04,0x08,0x10,0x7F,0x00 } , /* N  */
    { 0x3E,0x41,0x41,0x41,0x3E,0x00 } , /* O  */
    { 0x7F,0x09,0x09,0x09,0x06,0x00 } , /* P  */
    { 0x3E,0x41,0x51,0x21,0x5E,0x00 } , /* Q  */
    { 0x7F,0x09,0x19,0x29,0x46,0x00 } , /* R  */
    { 0x26,0x49,0x49,0x49,0x32,0x00 } , /* S  */
    { 0x01,0x01,0x7F,0x01,0x01,0x00 } , /* T  */
    { 0x3F,0x40,0x40,0x40,0x3F,0x00 } , /* U  */
    { 0x03,0x1C,0x60,0x1C,0x03,0x00 } , /* V  */
    { 0x0F,0x70,0x0F,0x70,0x0F,0x00 } , /* W  */
    { 0x41,0x36,0x08,0x36,0x41,0x00 } , /* X  */
    { 0x01,0x06,0x78,0x02,0x01,0x00 } , /* Y  */
    { 0x61,0x51,0x49,0x45,0x43,0x00 } , /* Z  */
    { 0x00,0x00,0x7F,0x41,0x41,0x00 } , /* [  */
    { 0x15,0x16,0x7C,0x16,0x11,0x00 } , /* \  */
    { 0x41,0x41,0x7F,0x00,0x00,0x00 } , /* ]  */
    { 0x00,0x02,0x01,0x02,0x00,0x00 } , /* ^  */
    { 0x40,0x40,0x40,0x40,0x40,0x00 } , /* _  */
    { 0x00,0x01,0x02,0x00,0x00,0x00 } , /* `  */
    { 0x00,0x20,0x54,0x54,0x78,0x00 } , /* a  */
    { 0x00,0x7F,0x44,0x44,0x38,0x00 } , /* b  */
    { 0x00,0x38,0x44,0x44,0x28,0x00 } , /* c  */
    { 0x00,0x38,0x44,0x44,0x7F,0x00 } , /* d  */
    { 0x00,0x38,0x54,0x54,0x18,0x00 } , /* e  */
    { 0x00,0x04,0x3E,0x05,0x01,0x00 } , /* f  */
    { 0x00,0x08,0x54,0x54,0x3C,0x00 } , /* g  */
    { 0x00,0x7F,0x04,0x04,0x78,0x00 } , /* h  */
    { 0x00,0x00,0x7D,0x00,0x00,0x00 } , /* i  */
    { 0x00,0x40,0x40,0x3D,0x00,0x00 } , /* j  */
    { 0x00,0x7F,0x10,0x28,0x44,0x00 } , /* k  */
    { 0x00,0x01,0x7F,0x00,0x00,0x00 } , /* l  */
    { 0x7C,0x04,0x7C,0x04,0x78,0x00 } , /* m  */
    { 0x00,0x7C,0x04,0x04,0x78,0x00 } , /* n  */
    { 0x00,0x38,0x44,0x44,0x38,0x00 } , /* o  */
    { 0x00,0x7C,0x14,0x14,0x08,0x00 } , /* p  */
    { 0x00,0x08,0x14,0x14,0x7C,0x00 } , /* q  */
    { 0x00,0x7C,0x08,0x04,0x04,0x00 } , /* r  */
    { 0x00,0x48,0x54,0x54,0x24,0x00 } , /* s  */
    { 0x00,0x04,0x3E,0x44,0x40,0x00 } , /* t  */
    { 0x00,0x3C,0x40,0x40,0x7C,0x00 } , /* u  */
    { 0x00,0x7C,0x20,0x10,0x0C,0x00 } , /* v  */
    { 0x1C,0x60,0x1C,0x60,0x1C,0x00 } , /* w  */
    { 0x00,0x6C,0x10,0x10,0x6C,0x00 } , /* x  */
    { 0x00,0x4C,0x50,0x30,0x1C,0x00 } , /* y  */
    { 0x00,0x44,0x64,0x54,0x4C,0x00 } , /* z  */
    { 0x00,0x08,0x36,0x41,0x41,0x00 } , /* {  */
    { 0x00,0x00,0x7F,0x00,0x00,0x00 } , /* |  */
    { 0x41,0x41,0x36,0x08,0x00,0x00 } , /* }  */
    { 0x08,0x04,0x08,0x10,0x08,0x00 } , /* ~  */
    { 0x00,0x00,0x00,0x00,0x00,0x00 }    /*null*/
};

ssd1331::ssd1331(PinName cs_pin, PinName rst_pin, PinName a0_pin, PinName mosi_pin, PinName miso_pin, PinName sclk_pin)
    : CS(cs_pin), RES(rst_pin), DC(a0_pin), spi(mosi_pin, miso_pin, sclk_pin)
{
    Init();
}

void ssd1331::Init(void)
{
    spi.format(8,3);
    spi.frequency(24000000);  // 12Mhz max for KL25z

    // reset
    ThisThread::sleep_for(200ms);
    RES = 0;       //Reset active
    ThisThread::sleep_for(200ms);
    RES = 1;

    // initialize sequence
    RegWrite(0xAE);    //OLED display OFF
    RegWrite(0x75);    /* Set Row Address */
    RegWrite(0x00);    /* Start = 0 */
    RegWrite(0x3F);    /* End = 63 */
    RegWrite(0x15);    /* Set Column Address */
    RegWrite(0x00);    /* Start = 0 */
    RegWrite(0x5F);    /* End = 95 */
    RegWrite(0xA0);    //Set remap & data format 0111 0000
    RegWrite(0x72);    // RGB colour
    RegWrite(0xA1);    //set display start row RAM
    RegWrite(0x00);
    RegWrite(0xA2);    //set dispaly offset
    RegWrite(0x00);
    RegWrite(0xA4);    //Set Display Mode
    RegWrite(0xA8);    //Set Multiplex Ratio
    RegWrite(0x3F);
    RegWrite(0xAD);    //Set Master Configuration
    RegWrite(0x8F);    //(External VCC Supply Selected)
    RegWrite(0xB0);    //Set Power Saving Mode
    RegWrite(0x1A);
    RegWrite(0xB1);    //Set Phase 1 & 2 Period Adjustment
    RegWrite(0x74);
    RegWrite(0xB3);    //Set Display Clock Divide Ratio / Oscillator Frequency
    RegWrite(0xD0);
    RegWrite(0x8A);    //Set Second Pre-charge Speed of Color A
    RegWrite(0x81);
    RegWrite(0x8B);    //Set Second Pre-charge Speed of Color B
    RegWrite(0x82);
    RegWrite(0x8C);    //Set Second Pre-charge Speed of Color C
    RegWrite(0x83);
    RegWrite(0xBB);    //Set Pre-charge Level
    RegWrite(0x3E);
    RegWrite(0xBE);    //Set VCOMH
    RegWrite(0x3E);
    RegWrite(0x87);    //Set Master Current Control
    RegWrite(0x0F);
    RegWrite(0x81);    //Set Contrast Control for Color &#129;gA&#129;h
    RegWrite(0x80);
    RegWrite(0x82);    //Set Contrast Control for Color &#129;gB&#129;h
    RegWrite(0x80);
    RegWrite(0x83);    //Set Contrast Control for Color &#129;gC&#129;h
    RegWrite(0x80);
    RegWrite(0xAF);    //display ON

    chr_size = NORMAL;
    cls();
}

void ssd1331::on()
{
    RegWrite(display_on);
}

void ssd1331::off()
{
    RegWrite(display_off);
}

void ssd1331::cls()
{
    unsigned char cmd[6]= {GAC_CLEAR_WINDOW,0,0,width,height};
    RegWriteM(cmd,5);
    wait_us(500);
    Maxwindow();
    background(0);
}

void ssd1331::set_font(unsigned char* f)
{
    font = f;
    if (font==NULL) {
        externalfont=0;   // set display.font
    } else {
        externalfont=1;
    }
}

void ssd1331::PutChar(uint8_t column,uint8_t row, int value)
{
    if(externalfont) { // external font
        uint8_t hor,vert,offset,bpl,j,i,b;
        const unsigned char* sign;
        unsigned char z,w;
        // read font parameter from start of array
        offset = font[0];                    // bytes / char
        hor = font[1];                       // get hor size of font
        vert = font[2];                      // get vert size of font
        bpl = font[3];                       // bytes per line
        if(value == '\n') {
            char_x = 0;
            char_y = char_y + vert;
        }
        if ((value < 31) || (value > 127)) return;   // test char range
        if (char_x + hor > 95) {
            char_x = 0;
            char_y = char_y + vert;
            if (char_y >= 63 - font[2]) {
                char_y = 0;
            }
        }
        window(char_x, char_y,hor,vert); 
        sign = &font[((value -32) * offset) + 4];
        w = sign[0];
        for (j=0; j<vert; j++) {
            for (i=0; i<hor; i++) {
                z =  sign[bpl * i + ((j & 0xF8) >> 3)+1];
                b = 1 << (j & 0x07);
                if (( z & b ) == 0x00) {
                    putp(BGround_Color);
                } else {
                    putp(Char_Color);
                }
            }
        }
        if ((w + 2) < hor) {    // x offset to next char
            char_x += w + 2;
        } else char_x += hor;
        
    } else {
        // internal font
        if(value == '\n') {
            char_x = 0;
            char_y = char_y + Y_height;
        }
        if ((value < 31) || (value > 127)) return;   // test char range
        if (char_x + X_width > width) {
            char_x = 0;
            char_y = char_y + Y_height;
            if (char_y >= height - Y_height) {
                char_y = 0;
            }
        }
        int i,j,w,lpx,lpy,k,l,xw;
        unsigned char Temp=0;
        j = 0; i = 0;
        w = X_width;
        FontSizeConvert(&lpx, &lpy);
        xw = X_width;
        
        for(i=0; i<xw; i++) {
            for ( l=0; l<lpx; l++) {
                Temp = font6x8[value-32][i];
                for(j=Y_height-1; j>=0; j--) {
                    for (k=0; k<lpy; k++) {
                        pixel(char_x+(i*lpx)+l, char_y+(((j+1)*lpy)-1)-k,  ((Temp & 0x80)==0x80) ? Char_Color : BGround_Color);
                    }
                    Temp = Temp << 1;
                }
            }
        }
        FontSizeConvert(&lpx, &lpy);
        char_x += (w*lpx);
    }
}

void ssd1331::dim()
{
    unsigned char cmd[5]= {GAC_DIM_WINDOW,0,0,width,height};
    RegWriteM(cmd,5);
}

void ssd1331::contrast(char value)
{
    int v = value*20;
    if(v>180) {
        v=180;
    }
    unsigned char cmd[7];
    cmd[0] = contrastA;
    cmd[1] = v;
    cmd[2] = contrastB;
    cmd[3] = v;
    cmd[4] = contrastC;
    cmd[5] = v;
    RegWriteM(cmd, 6);
}

uint16_t ssd1331::toRGB(uint16_t R,uint16_t G,uint16_t B)
{  
    uint16_t c;
    c = R >> 3;
    c <<= 6;
    c |= G >> 2;
    c <<= 5;
    c |= B >> 3;
    return c;
}

void ssd1331::rect(uint8_t x1,uint8_t y1,uint8_t x2,uint8_t y2,uint16_t colorline)
{
    if  ( x1 > width ) x1 = width;
    if  ( y1 > height ) y1 = height;
    if  ( x2 > width ) x2 = width;
    if  ( y2 > height ) y2 = height;

    unsigned char cmd[11]= { 0 };
    cmd[0] = GAC_FILL_ENABLE_DISABLE;
    cmd[1] = 0;      // fill 1, empty 0
    RegWriteM(cmd, 2);
    cmd[0] = GAC_DRAW_RECTANGLE;
    cmd[1] = (unsigned char)x1;
    cmd[2] = (unsigned char)y1;
    cmd[3] = (unsigned char)x2;
    cmd[4] = (unsigned char)y2;
    cmd[5] = (unsigned char)((colorline>> 11) << 1);    // Outline Blue
    cmd[6] = (unsigned char)((colorline>> 5 ) & 0x3F);  // Outline Green
    cmd[7] = (unsigned char)((colorline<< 1 ) & 0x3F);  // Outline Red
    cmd[8] = (0);
    cmd[9] = (0);
    cmd[10]= (0);
    RegWriteM(cmd, 11);
    wait_us(500);
}

void ssd1331::fillrect(uint8_t x1,uint8_t y1,uint8_t x2,uint8_t y2,uint16_t colorline,uint16_t colorfill)
{
    if  ( x1 > width ) x1 = width;
    if  ( y1 > height ) y1 = height;
    if  ( x2 > width ) x2 = width;
    if  ( y2 > height ) y2 = height;

    unsigned char cmd[11]= { 0 };
    cmd[0] = GAC_FILL_ENABLE_DISABLE;
    cmd[1] = 1;      // fill 1, empty 0
    RegWriteM(cmd, 2);
    cmd[0] = GAC_DRAW_RECTANGLE;
    cmd[1] = (unsigned char)x1;
    cmd[2] = (unsigned char)y1;
    cmd[3] = (unsigned char)x2;
    cmd[4] = (unsigned char)y2;
    cmd[5] = (unsigned char)((colorline>> 11) << 1);    // Outline Blue
    cmd[6] = (unsigned char)((colorline>> 5 ) & 0x3F);  // Outline Green
    cmd[7] = (unsigned char)((colorline<< 1 ) & 0x3F);  // Outline Red
    cmd[8] = (unsigned char)((colorfill>> 11) << 1);    // fill Blue
    cmd[9] = (unsigned char)((colorfill>> 5 ) & 0x3F);  // fill Green
    cmd[10]= (unsigned char)((colorfill<< 1 ) & 0x3F);  // fill Red
    RegWriteM(cmd, 11);
    wait_us(500);
}

void ssd1331::line(uint8_t x1,uint8_t y1,uint8_t x2,uint8_t y2,uint16_t color)
{
    if  ( x1 > width ) x1 = width;
    if  ( y1 > height ) y1 = height;
    if  ( x2 > width ) x2 = width;
    if  ( y2 > height ) y2 = height;

    unsigned char cmd[11]= { 0 };
    cmd[0] = GAC_FILL_ENABLE_DISABLE;
    cmd[1] = 0;      // fill 0, empty 0
    RegWriteM(cmd, 2);
    cmd[0] = GAC_DRAW_LINE;
    cmd[1] = (unsigned char)x1;
    cmd[2] = (unsigned char)y1;
    cmd[3] = (unsigned char)x2;
    cmd[4] = (unsigned char)y2;
    cmd[5] = (unsigned char)(((color>>11)&0x1F)<<1);    // Blue
    cmd[6] = (unsigned char)((color>>5)&0x3F);          // Green
    cmd[7] = (unsigned char)((color&0x1F)<<1);          // Red
    RegWriteM(cmd, 8);
    wait_us(500);
}

void ssd1331::circle (uint8_t radius, uint8_t x, uint8_t y , uint16_t col, uint16_t fill)
{
    if  ( x > width ) x = width;
    if  ( y > height ) y = height;
    
    int16_t  cx, cy, d;
    d = 3 - 2 * radius;
    cy = radius;
    pixel(x, radius+y, col);
    pixel(x, -radius+y, col);
    pixel(radius+x, y, col);
    pixel(-radius+x, y, col);
    if(fill) {
        line(x,radius+y,x,-radius+y,col);
        line( radius+x,y,-radius+x,y,col);
    }

    for (cx = 0; cx <= cy; cx++) {
        if(d>=0) {
            d+=10+4*cx-4*cy;
            cy--;
        } else {
            d+=6+4*cx;
        }
        pixel(cy+x, cx+y, col);
        pixel(cx+x, cy+y, col);
        pixel(-cx+x, cy+y, col);
        pixel(-cy+x, cx+y, col);
        pixel(-cy+x, -cx+y, col);
        pixel(-cx+x, -cy+y, col);
        pixel(cx+x, -cy+y, col);
        pixel(cy+x, -cx+y, col);
        if(fill) {
            line(cy+x, cx+y, cy+x, -cx+y, col);
            line(cx+x, cy+y, cx+x, -cy + y, col);
            line(-cx+x, cy+y, -cx+x, cy+y, col);
            line(-cy+x, cx+y, -cy+x, cx+y, col);
            line(-cy+x, -cx+y, -cy+x, cx+y, col);
            line(-cx+x, -cy+y, -cx+x, cy+y, col);
            line(cx+x, -cy+y, cx+x, cy+y, col);
            line(cy+x, -cx+y, cy+x, cx+y, col);
        }
    }
}

void ssd1331::ScrollSet(int8_t horizontal, int8_t startline, int8_t linecount, int8_t vertical , int8_t frame_interval)
{
    unsigned char cmd[7];
    if((startline>height+1)||((startline+linecount)>height+1)) return ;
    if ( frame_interval > 3 ) frame_interval = 3;
    cmd[0] = SCROLL_SETUP;      //
    cmd[1] = horizontal;
    cmd[2] = startline;
    cmd[3] = linecount;
    cmd[4] = vertical;
    cmd[5] = frame_interval;
    RegWriteM(cmd,6);
}

void ssd1331::Bitmap(const uint8_t *bitmap, uint8_t x, uint8_t y, uint8_t w, uint8_t h, unsigned char color) {
 
    window(x, y, w, h);
    int16_t i, j, byteWidth = (w + 7) / 8; 
    for(j=0; j<h; j++) {
        for(i=0; i<w; i++ ) {
            if(bitmap[ j * byteWidth + i / 8] & (128 >> (i & 7))) {
                pixel(x+i, y+j, color);
            }
        }
    }
    Maxwindow();
}

void ssd1331::Bitmap16(uint8_t x, uint8_t y, uint8_t w, uint8_t h, const uint8_t  *bitmap)
{
    int8_t  i,j;
    int8_t padd;
    unsigned short *bitmap_ptr = (unsigned short *)bitmap;
    
    window(x, y, w, h);    
    // the lines are padded to multiple of 4 bytes in a bitmap
    padd = -1;
    do {
        padd ++;
    } while (2*(w + padd)%4 != 0);
    
    window(x, y, w, h);
    
    bitmap_ptr += ((h - 1)* (w + padd));
    
    for (j = 0; j < h; j++) {         //Lines
        for (i = 0; i < w; i++) {     // one line
                DataWrite_to(*bitmap_ptr);
                bitmap_ptr++;
        }
        bitmap_ptr -= 2*w;
        bitmap_ptr -= padd;
    }
    Maxwindow();
}

int ssd1331::Bitmap16RAM(uint8_t x, uint8_t y, unsigned char *Name_BMP)
{   
    #define OffsetPixelWidth    18
    #define OffsetPixelHeigh    22
    #define OffsetFileSize      34
    #define OffsetPixData       10
    #define OffsetBPP           28
    char filename[50];
    unsigned char BMP_Header[54];
    unsigned short BPP_t;
    unsigned int PixelWidth,PixelHeigh,start_data;
    char * buffer;
    size_t result;
    int fileSize,padd,i,j;
     
    i=0;
    while (*Name_BMP!='\0') {
        filename[i++]=*Name_BMP++;
    } 
    
    filename[i] = 0; 
    FILE *Image = fopen((const char *)&filename[0], "rb");  // open the bmp file
    if (!Image) {
        return(0);      // error file not found !
    }
    
    fread(&BMP_Header[0],1,54,Image);      // get the BMP Header

    if (BMP_Header[0] != 0x42 || BMP_Header[1] != 0x4D) {  // check magic byte
        fclose(Image);
        return(-1);     // error not BMP file
    }
    
    BPP_t = BMP_Header[OffsetBPP] + (BMP_Header[OffsetBPP + 1] << 8);
    if (BPP_t != 0x0010) {
        fclose(Image);
        return(-2);     // error not 16 bit BMP
    }
    PixelHeigh = BMP_Header[OffsetPixelHeigh] + (BMP_Header[OffsetPixelHeigh + 1] << 8) + (BMP_Header[OffsetPixelHeigh + 2] << 16) + (BMP_Header[OffsetPixelHeigh + 3] << 24);
    PixelWidth = BMP_Header[OffsetPixelWidth] + (BMP_Header[OffsetPixelWidth + 1] << 8) + (BMP_Header[OffsetPixelWidth + 2] << 16) + (BMP_Header[OffsetPixelWidth + 3] << 24);
    if (PixelHeigh > height+1 + y || PixelWidth > width+1 + x) {
        fclose(Image);
        return(-3);      // to big
    }
    
    start_data = BMP_Header[OffsetPixData] + (BMP_Header[OffsetPixData + 1] << 8) + (BMP_Header[OffsetPixData + 2] << 16) + (BMP_Header[OffsetPixData + 3] << 24);
    
    // obtain file size:
    fseek (Image , 0 , SEEK_END);
    fileSize = ftell (Image)-start_data;
    std::rewind (Image);
    
    // allocate memory to contain the whole file:
    buffer = (char*) malloc (sizeof(char)*fileSize/2);
    if (buffer == NULL) {return (fileSize/2);}
    
    // copy the file into the buffer:
    fseek (Image, start_data , SEEK_SET );  // set SD file data start position    
    result = fread (buffer,1,fileSize,Image);
    fclose (Image);
    if (result != fileSize) {return (-5);}   
    
    unsigned short *bitmap_ptr = (unsigned short *)buffer;    
          
    // the lines are padded to multiple of 4 bytes in a bitmap
    padd = -1;
    do {
        padd ++;
    } while (2*(PixelWidth + padd)%4 != 0);
     
    bitmap_ptr += ((PixelHeigh - 1)* (PixelWidth + padd));
   
    window(x, y, PixelWidth, PixelHeigh);
    
    for (j = 0; j < PixelHeigh; j++) {         //Lines
        for (i = 0; i < PixelWidth; i++) {     // one line
                DataWrite_to(*bitmap_ptr);
                bitmap_ptr++;
        }
        bitmap_ptr -= 2*PixelWidth ;
        bitmap_ptr -= padd;
    }
    // terminate
    free (buffer);
    Maxwindow();
    return (fileSize);
}

int ssd1331::Bitmap16FS(uint8_t x, uint8_t y, unsigned char *Name_BMP) {
#define OffsetPixelWidth    18
#define OffsetPixelHeigh    22
#define OffsetFileSize      34
#define OffsetPixData       10
#define OffsetBPP           28
    char filename[50];
    unsigned char BMP_Header[54];
    unsigned short BPP_t;
    unsigned int PixelWidth,PixelHeigh,start_data;
    unsigned int    i,off;
    int padd,j;
    unsigned short *line;
    
    i=0;
    while (*Name_BMP!='\0') {
        filename[i++]=*Name_BMP++;
    } 
    
    filename[i] = 0; 
    FILE *Image = fopen((const char *)&filename[0], "rb");  // open the bmp file
    if (!Image) {
        return(0);      // error file not found !
    }
    
    fread(&BMP_Header[0],1,54,Image);      // get the BMP Header

    if (BMP_Header[0] != 0x42 || BMP_Header[1] != 0x4D) {  // check magic byte
        fclose(Image);
        return(-1);     // error no BMP file
    }
    BPP_t = BMP_Header[OffsetBPP] + (BMP_Header[OffsetBPP + 1] << 8);
    if (BPP_t != 0x0010) {
        fclose(Image);
        return(-2);     // error no 16 bit BMP
    }
    PixelHeigh = BMP_Header[OffsetPixelHeigh] + (BMP_Header[OffsetPixelHeigh + 1] << 8) + (BMP_Header[OffsetPixelHeigh + 2] << 16) + (BMP_Header[OffsetPixelHeigh + 3] << 24);
    PixelWidth = BMP_Header[OffsetPixelWidth] + (BMP_Header[OffsetPixelWidth + 1] << 8) + (BMP_Header[OffsetPixelWidth + 2] << 16) + (BMP_Header[OffsetPixelWidth + 3] << 24);
    if (PixelHeigh > height+1 + y || PixelWidth > width+1 + x) {
        fclose(Image);
        return(-3);      // to big
    }
    start_data = BMP_Header[OffsetPixData] + (BMP_Header[OffsetPixData + 1] << 8) + (BMP_Header[OffsetPixData + 2] << 16) + (BMP_Header[OffsetPixData + 3] << 24);

    line = (unsigned short *) malloc (PixelWidth); // we need a buffer for a line
    if (line == NULL) {
        return(-4);         // error no memory
    }
    // the lines are padded to multiple of 4 bytes
    padd = -1;
    do {
        padd ++;
    } while ((PixelWidth * 2 + padd)%4 != 0);
    
    window(x, y,PixelWidth,PixelHeigh);
   
    for (j = PixelHeigh - 1; j >= 0; j--) {               //Lines bottom up
        off = j * (PixelWidth * 2 + padd) + start_data;   // start of line
        fseek(Image, off ,SEEK_SET);
        fread(line,1,PixelWidth * 2,Image);       // read a line - slow !
        for (i = 0; i < PixelWidth; i++) {        // copy pixel data to TFT
             DataWrite_to(line[i]);
        } 
    }
    free (line);
    fclose(Image);
    Maxwindow();
    return(PixelWidth);
}

void ssd1331::Copy(uint8_t src_x1,uint8_t src_y1,uint8_t src_x2,uint8_t src_y2,uint8_t dst_x,uint8_t dst_y)
{
    unsigned char cmd[8]= { 0 };
    if ((src_x1>width)||(src_y1>height)||(src_x2>width)||(src_y2>height)) return;
    if ((dst_x>width)||(dst_y>height))return;
    cmd[0] = GAC_COPY_AREA;      //
    cmd[1] = (unsigned char)src_x1;
    cmd[2] = (unsigned char)src_y1;
    cmd[3] = (unsigned char)src_x2;
    cmd[4] = (unsigned char)src_y2;
    cmd[5] = (unsigned char)dst_x;
    cmd[6] = (unsigned char)dst_y;
    RegWriteM(cmd,7);
}

void ssd1331::Fill_Screen(uint16_t color)
{
    BGround_Color = color;
    fillrect(0,0,width,height,color,color);
}

void ssd1331::locate(uint8_t column, uint8_t row)
{
    char_x  = column;
    char_y = row;
}

void ssd1331::foreground(uint16_t color)
{
    Char_Color = color;
}
void ssd1331::background(uint16_t color)
{
    BGround_Color = color;
}

void ssd1331::SetFontSize(uint8_t Csize)
{
    chr_size = Csize;
}

void ssd1331::putp(int colour)
{
    pixel(_x, _y, colour);
    _x++;
    if(_x > _x2) {
        _x = _x1;
        _y++;
        if(_y > _y2) {
            _y = _y1;
        }
    }
}

int ssd1331::_putc( int c )
{    
    PutChar( char_x , char_y ,c);
    return c;
}

void ssd1331::pixel(uint8_t x,uint8_t y,uint16_t Color)
{
    unsigned char cmd[7]= {Set_Column_Address,0x00,0x00,Set_Row_Address,0x00,0x00};
    if ((x>width)||(y>height)) return ;
    cmd[1] = (unsigned char)x;
    cmd[2] = (unsigned char)x;
    cmd[4] = (unsigned char)y;
    cmd[5] = (unsigned char)y;
    RegWriteM(cmd, 6);
    DataWrite_to(Color);
}

void ssd1331::Maxwindow()
{    
    unsigned char cmd[7]= {Set_Column_Address,0x00,0x5F,Set_Row_Address,0x00,0x3F};
    RegWriteM(cmd, 6);
}

void ssd1331::window(uint8_t x, uint8_t y, uint8_t w, uint8_t h)
{
    _x = x;
    _y = y;
    // window settings
    _x1 = x;            // start y
    _x2 = x + w - 1;    // end x
    _y1 = y;            // start y
    _y2 = y + h - 1;    // end y
    unsigned char cmd[7]= {Set_Column_Address,0x00,0x00,Set_Row_Address,0x00,0x00};
    RegWriteM(cmd, 6);
    unsigned char cmd2[7]= {Set_Column_Address,_x1,_x2,Set_Row_Address,_y1,_y2};
    RegWriteM(cmd2, 6);
}

void ssd1331::Scrollstart()
{
    RegWrite(SCROLL_START);
}

void ssd1331::Scrollstop()
{
    RegWrite(SCROLL_STOP);
}

int ssd1331::_getc()
{
    return -1;
}

uint8_t ssd1331::row()
{
    return char_y;
}
uint8_t ssd1331::column()
{
    return char_x;
}

void ssd1331::FontSizeConvert(int *lpx,int *lpy)
{
    switch( chr_size ) {
        case WIDE:
            *lpx=2;
            *lpy=1;
            break;
        case HIGH:
            *lpx=1;
            *lpy=2;
            break;
        case WH  :
            *lpx=2;
            *lpy=2;
            break;
        case WHx36  :
            *lpx=6;
            *lpy=6;
            break;
        case NORMAL:
        default:
            *lpx=1;
            *lpy=1;
            break;
    }
}

void  ssd1331::RegWrite(unsigned char Command)
{
    DC = 0;     // Command
    CS = 0;     // CS enable
    spi.write(Command);
    CS = 1;     // CS dissable
}

void  ssd1331::RegWriteM(unsigned char *Command, uint8_t count)
{
    int i;
    DC = 0;     // Command
    CS = 0;     // CS enable
    for( i=0; i<count; i++) {
        spi.write(*Command++);
    }
    CS = 1;     // CS dissable
}

void  ssd1331::DataWrite(unsigned char c)
{
    DC = 1;    // DATA
    CS = 0;    // CS enable
    spi.write(c);
    CS = 1;    // CS dissable
}

void  ssd1331::DataWrite_to(uint16_t Dat)
{
    DC = 1;    // DATA
    CS = 0;    // CS enable    
    spi.write((unsigned char)((Dat >> 8)));
    spi.write((unsigned char)(Dat));
    CS = 1;    // CS dissable
}





