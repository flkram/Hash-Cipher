#include <iostream>
#include <iomanip>
#include <cryptlib.h>
#include <whirlpool.h>
#include <openssl/whirlpool.h>
#include <string.h>
extern "C" {
    const char* hashWhirlpool(const char* input) {
        static unsigned char hash[WHIRLPOOL_DIGEST_LENGTH];
        WHIRLPOOL_CTX whirlpoolContext;
        WHIRLPOOL_Init(&whirlpoolContext);
        WHIRLPOOL_Update(&whirlpoolContext, input, strlen(input));
        WHIRLPOOL_Final(hash, &whirlpoolContext);

        static char hexOutput[129];
        for (int i = 0; i < WHIRLPOOL_DIGEST_LENGTH; ++i) {
            sprintf(hexOutput + (i * 2), "%02x", hash[i]);
        }
        hexOutput[128] = 0;  // Null-terminate the string
        return hexOutput;
    }
}

std::string whirlpool_hash(const std::string &input) {
    using namespace CryptoPP;

    // Initialize the Whirlpool hash function
    Whirlpool hash;

    // Create a hash object to hold the result
    byte digest[Whirlpool::DIGESTSIZE];

    // Compute the hash
    hash.CalculateDigest(digest, (const byte*)input.c_str(), input.length());

    // Convert the byte array into a hexadecimal string
    std::stringstream ss;
    for (int i = 0; i < Whirlpool::DIGESTSIZE; i++) {
        ss << std::setw(2) << std::setfill('0') << std::hex << (int)digest[i];
    }

    return ss.str();
}

int main() {
    // Input string
    std::string input;
    std::cout << "Enter a string to hash: ";
    std::getline(std::cin, input);

    // Get the Whirlpool hash
    std::string hash = whirlpool_hash(input);

    // Output the result
    std::cout << "Whirlpool Hash: " << hash << std::endl;

    return 0;
}
