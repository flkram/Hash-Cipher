#include <iostream>
#include <iomanip>
#include <openssl/sha.h>
#include <openssl/sha.h>
#include <string.h>
extern "C" {
    const char* hashSHA3(const char* input) {
        static unsigned char hash[SHA3_256_DIGEST_LENGTH];
        SHA3_CTX sha3Context;
        SHA3_Init(&sha3Context, SHA3_256);
        SHA3_Update(&sha3Context, input, strlen(input));
        SHA3_Final(hash, &sha3Context);

        static char hexOutput[65];
        for (int i = 0; i < SHA3_256_DIGEST_LENGTH; ++i) {
            sprintf(hexOutput + (i * 2), "%02x", hash[i]);
        }
        hexOutput[64] = 0;  // Null-terminate the string
        return hexOutput;
    }
}

std::string sha3_256(const std::string &input) {
    // Create a SHA256 context
    unsigned char hash[SHA256_DIGEST_LENGTH];

    // Compute the SHA-256 hash of the input
    SHA256_CTX sha256_ctx;
    SHA256_Init(&sha256_ctx);
    SHA256_Update(&sha256_ctx, input.c_str(), input.length());
    SHA256_Final(hash, &sha256_ctx);

    // Convert the hash to a string
    std::stringstream ss;
    for (int i = 0; i < SHA256_DIGEST_LENGTH; i++) {
        ss << std::setw(2) << std::setfill('0') << std::hex << (int)hash[i];
    }

    return ss.str();
}

int main() {
    // Input string
    std::string input;
    std::cout << "Enter a string to hash: ";
    std::getline(std::cin, input);

    // Get the SHA-3 hash
    std::string hash = sha3_256(input);

    // Output the result
    std::cout << "SHA-3 Hash: " << hash << std::endl;

    return 0;
}
