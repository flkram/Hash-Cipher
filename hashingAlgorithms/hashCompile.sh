g++ -shared -o libhashMD5.so -fPIC hashMD5.cpp
g++ -shared -o libhashSHA256.so -fPIC hashSHA256.cpp
g++ -shared -o libhashSHA3.so -fPIC hashSHA3.cpp -lssl -lcrypto
g++ -shared -o libhashWhirlpool.so -fPIC hashWhirlpool.cpp -lssl -lcrypto
