#include <iostream>
#include <vector>
#include <string>
#include <iomanip>
#include <sstream>
#include <cstring>
#include <string.h>
extern "C" {
    const char* hashSHA256(const char* input) {
        static unsigned char hash[SHA256_DIGEST_LENGTH];
        SHA256_CTX sha256Context;
        SHA256_Init(&sha256Context);
        SHA256_Update(&sha256Context, input, strlen(input));
        SHA256_Final(hash, &sha256Context);

        static char hexOutput[65];
        for (int i = 0; i < SHA256_DIGEST_LENGTH; ++i) {
            sprintf(hexOutput + (i * 2), "%02x", hash[i]);
        }
        hexOutput[64] = 0;  // Null-terminate the string
        return hexOutput;
    }
}

// Define constants
typedef uint32_t word;
const int HASH_WORDS = 8;
const int BLOCK_SIZE = 64;
const int BBITS = 8; // bits in a byte
const int SIZE_DIVISOR = 256;
const int ROW_LEN = 4; // size of each word
const int INIT_W_LEN = 16;
const word initial_h[HASH_WORDS] = {
    0x6a09e667, 0xbb67ae85, 0x3c6ef372, 0xa54ff53a,
    0x510e527f, 0x9b05688c, 0x1f83d9ab, 0x5be0cd19
};
const word constant_k[64] = {
    0x428a2f98, 0x71374491, 0xb5c0fbcf, 0xe9b5dba5,
    0x3956c25b, 0x59f111f1, 0x923f82a4, 0xab1c5ed5,
    0xd807aa98, 0x12835b01, 0x243185be, 0x550c7dc3,
    0x72be5d74, 0x80deb1fe, 0x9bdc06a7, 0xc19bf174,
    0xe49b69c1, 0xefbe4786, 0x0fc19dc6, 0x240ca1cc,
    0x2de92c6f, 0x4a7484aa, 0x5cb0a9dc, 0x76f988da,
    0x983e5152, 0xa831c66d, 0xb00327c8, 0xbf597fc7,
    0xc6e00bf3, 0xd5a79147, 0x06ca6351, 0x14292967,
    0x27b70a85, 0x2e1b2138, 0x4d2c6dfc, 0x53380d13,
    0x650a7354, 0x766a0abb, 0x81c2c92e, 0x92722c85,
    0xa2bfe8a1, 0xa81a664b, 0xc24b8b70, 0xc76c51a3,
    0xd192e819, 0xd6990624, 0xf40e3585, 0x106aa070,
    0x19a4c116, 0x1e376c08, 0x2748774c, 0x34b0bcb5,
    0x391c0cb3, 0x4ed8aa4a, 0x5b9cca4f, 0x682e6ff3,
    0x748f82ee, 0x78a5636f, 0x84c87814, 0x8cc70208,
    0x90befffa, 0xa4506ceb, 0xbef9a3f7, 0xc67178f2
};

// Helper function to rotate bits
word rotate(word val, int bits) {
    return ((val >> bits) | (val << (32 - bits)));
}

// Helper function for the Sigma0 transformation
word Sigma0(word a) {
    return (rotate(a, 2) ^ rotate(a, 13) ^ rotate(a, 22));
}

// Helper function for the Sigma1 transformation
word Sigma1(word a) {
    return (rotate(a, 6) ^ rotate(a, 11) ^ rotate(a, 25));
}

// Ch function
word ChFunction(word e, word f, word g) {
    return ((e & f) ^ (~e & g));
}

// Ma function
word MaFunction(word a, word b, word c) {
    return ((a & b) ^ (a & c) ^ (b & c));
}

// Compute the SHA-256 compression round
void computeRound(word h[HASH_WORDS], word w[BLOCK_SIZE], int n) {
    word newE, newA;
    word parsedValue = ChFunction(h[4], h[5], h[6]);
    parsedValue += h[7] + w[n] + constant_k[n];
    parsedValue += Sigma1(h[4]);
    newE = parsedValue + h[3];

    parsedValue += MaFunction(h[0], h[1], h[2]);
    parsedValue += Sigma0(h[0]);
    newA = parsedValue;

    for (int i = HASH_WORDS - 1; i >= 0; --i) {
        if (i == 4) {
            h[i] = newE;
        } else if (i == 0) {
            h[i] = newA;
        } else {
            h[i] = h[i - 1];
        }
    }
}

// Extend the message to 64 words
void extendMessage(const std::vector<uint8_t>& block, word w[BLOCK_SIZE]) {
    for (int i = 0; i < 16; ++i) {
        w[i] = (block[i * 4] << 24) | (block[i * 4 + 1] << 16) |
               (block[i * 4 + 2] << 8) | block[i * 4 + 3];
    }

    for (int i = 16; i < 64; ++i) {
        w[i] = (rotate(w[i - 15], 7) ^ rotate(w[i - 15], 18) ^ (w[i - 15] >> 3)) +
               (rotate(w[i - 2], 17) ^ rotate(w[i - 2], 19) ^ (w[i - 2] >> 10)) +
               w[i - 7] + w[i - 16];
    }
}

// SHA-256 padding and compression
void sha256(const std::string& input, std::string& output) {
    std::vector<uint8_t> data(input.begin(), input.end());
    data.push_back(0x80);

    while ((data.size() % 64) != 56) {
        data.push_back(0x00);
    }

    uint64_t bit_length = static_cast<uint64_t>(input.size()) * 8;
    for (int i = 0; i < 8; ++i) {
        data.push_back(static_cast<uint8_t>((bit_length >> (56 - 8 * i)) & 0xFF));
    }

    word h[HASH_WORDS];
    std::memcpy(h, initial_h, sizeof(initial_h));

    word w[BLOCK_SIZE];

    for (size_t i = 0; i < data.size(); i += BLOCK_SIZE) {
        std::vector<uint8_t> block(data.begin() + i, data.begin() + i + BLOCK_SIZE);
        extendMessage(block, w);
        for (int j = 0; j < 64; ++j) {
            computeRound(h, w, j);
        }
    }

    std::stringstream ss;
    for (int i = 0; i < HASH_WORDS; ++i) {
        ss << std::setw(8) << std::setfill('0') << std::hex << h[i];
    }
    output = ss.str();
}

int main() {
    std::string input = "hello world";
    std::string output;

    sha256(input, output);

    std::cout << "SHA-256 hash: " << output << std::endl;

    return 0;
}
