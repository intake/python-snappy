// check snappy version

#include <iostream>
#include "snappy-stubs-public.h"

int main(int argc, char **argv){
    std::cout << SNAPPY_VERSION;
    return 0;
}