#include <iostream>
#include <sstream>
#include <iomanip>
#include <cstring>
#include <openssl/md5.h>

#define MD5_DIGEST_LENGTH 16

// extern "C" {
//     const char* hashMD5(const char* input) {
//         unsigned char result[MD5_DIGEST_LENGTH];
//         MD5_CTX md5Context;
//         MD5_Init(&md5Context);
//         MD5_Update(&md5Context, input, strlen(input));
//         MD5_Final(result, &md5Context);

//         static char hexOutput[33];
//         for (int i = 0; i < MD5_DIGEST_LENGTH; ++i) {
//             sprintf(hexOutput + (i * 2), "%02x", result[i]);
//         }
//         hexOutput[32] = 0;
//         return hexOutput;
//     }
// }

class MD5 {
private:
    static const unsigned int s[64];
    static const unsigned int K[64];
    
    static unsigned int F(unsigned int b, unsigned int c, unsigned int d) {
        return (b & c) | (~b & d);
    }
    
    static unsigned int G(unsigned int b, unsigned int c, unsigned int d) {
        return (b & d) | (c & ~d);
    }
    
    static unsigned int H(unsigned int b, unsigned int c, unsigned int d) {
        return b ^ c ^ d;
    }
    
    static unsigned int I(unsigned int b, unsigned int c, unsigned int d) {
        return c ^ (b | ~d);
    }

    static void transform(unsigned int state[4], unsigned char block[64]) {
        unsigned int a = state[0], b = state[1], c = state[2], d = state[3];
        unsigned int x[16];
        
        for (int i = 0; i < 16; i++) {
            x[i] = (block[i * 4]) | (block[i * 4 + 1] << 8) | (block[i * 4 + 2] << 16) | (block[i * 4 + 3] << 24);
        }

        unsigned int temp;
        
        for (int i = 0; i < 64; i++) {
            if (i < 16) {
                temp = F(b, c, d) + a + x[i] + K[i];
            } else if (i < 32) {
                temp = G(b, c, d) + a + x[(5 * i + 1) % 16] + K[i];
            } else if (i < 48) {
                temp = H(b, c, d) + a + x[(3 * i + 5) % 16] + K[i];
            } else {
                temp = I(b, c, d) + a + x[(7 * i) % 16] + K[i];
            }
            
            temp = (temp << s[i]) | (temp >> (32 - s[i]));
            a = d;
            d = c;
            c = b;
            b = b + temp;
        }

        state[0] += a;
        state[1] += b;
        state[2] += c;
        state[3] += d;
    }

public:
    static void MD5Init(unsigned int state[4]) {
        state[0] = 0x67452301;
        state[1] = 0xEFCDAB89;
        state[2] = 0x98BADCFE;
        state[3] = 0x10325476;
    }

    static void MD5Update(unsigned int state[4], unsigned int count[2], unsigned char buffer[64], const unsigned char *input, size_t length) {
        size_t i, index, partLen;
        index = (count[0] >> 3) & 0x3F;
        partLen = 64 - index;
        
        count[0] += length << 3;
        if (count[0] < (length << 3)) {
            count[1]++;
        }
        count[1] += length >> 29;

        if (length >= partLen) {
            memcpy(&buffer[index], input, partLen);
            transform(state, buffer);

            for (i = partLen; i + 63 < length; i += 64) {
                transform(state, (unsigned char*)&input[i]);
            }

            index = 0;
        } else {
            i = 0;
        }

        memcpy(&buffer[index], &input[i], length - i);
    }

    static void MD5Final(unsigned int state[4], unsigned int count[2], unsigned char buffer[64], unsigned char digest[16]) {
        unsigned char padding[64] = { 0x80 };
        unsigned char length[8];
        unsigned int index, padLen;

        for (int i = 0; i < 8; i++) {
            length[i] = (count[i >> 3] >> ((i % 8) * 8)) & 0xFF;
        }

        index = (count[0] >> 3) & 0x3F;
        padLen = (index < 56) ? (56 - index) : (120 - index);
        MD5Update(state, count, buffer, padding, padLen);
        MD5Update(state, count, buffer, length, 8);

        for (int i = 0; i < 4; i++) {
            digest[i] = (state[i] & 0xFF);
            digest[i + 4] = (state[i] >> 8) & 0xFF;
            digest[i + 8] = (state[i] >> 16) & 0xFF;
            digest[i + 12] = (state[i] >> 24) & 0xFF;
        }
    }

    static void stringToMD5(const std::string &input, std::string &output) {
        unsigned int state[4];
        unsigned int count[2] = { 0, 0 };
        unsigned char buffer[64];
        unsigned char digest[16];

        MD5Init(state);
        MD5Update(state, count, buffer, (const unsigned char *)input.c_str(), input.length());
        MD5Final(state, count, buffer, digest);

        std::stringstream ss;
        for (int i = 0; i < 16; i++) {
            ss << std::setw(2) << std::setfill('0') << std::hex << (int)digest[i];
        }
        output = ss.str();
    }
};

const unsigned int MD5::K[64] = {
    0xd76aa478, 0xe8c7b756, 0x242070db, 0xc1bdceee, 0xf57c0faf, 0x4787c62a, 0xa8304613, 0xfd469501,
    0x698098d8, 0x8b44f7af, 0xffff5bb1, 0x895cd7be, 0x6b901122, 0xfd987193, 0xa679438e, 0x49b40821,
    0x243185be, 0x3b8b1d4c, 0x575f6b5f, 0x6fa87e4f, 0x8d7d2e81, 0x14a3a9a2, 0x3d2c6ec2, 0x4d2a702d,
    0x7e40d6d0, 0x7e84bc54, 0x4a7e49f5, 0x1676e8fd, 0xe64b73ff, 0x48f16932, 0x62c9eb67, 0x778f99ea,
    0x128035fa, 0x5352543b, 0x82e983cf, 0x7d4bdb3e, 0x39652e7d, 0x9edb81ea, 0x3f1bc17d, 0x2d95d1a3,
    0x98e05878, 0x0ba775c1, 0x90b6c1e2, 0x7099d275, 0x4e6b039c, 0x60f6b57e, 0x42c40a13, 0xf806b13d,
};

const unsigned int MD5::s[64] = {
    7, 12, 17, 22, 7, 12, 17, 22, 7, 12, 17, 22, 7, 12, 17, 22,
    5, 9, 14, 20, 5, 9, 14, 20, 5, 9, 14, 20, 5, 9, 14, 20,
    4, 11, 16, 23, 4, 11, 16, 23, 4, 11, 16, 23, 4, 11, 16, 23,
    6, 10, 15, 21, 6, 10, 15, 21, 6, 10, 15, 21, 6, 10, 15, 21
};

int main(int argc, char *argv[]) {
    std::string input = "";
    if (argc>1){
        input = argv[1];
    }
    std::string output;

    MD5::stringToMD5(input, output);

    std::cout << "MD5: " << output << std::endl;

    return 0;
}