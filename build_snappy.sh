git clone --depth 1 --branch 1.1.8 https://github.com/google/snappy snappy-src
cd snappy-src 
git submodule update --init


case "$(uname -s)" in
   CYGWIN*|MINGW32*|MSYS*|MINGW*)
    cmake -G "Visual Studio 16 2019" -A Win32 -S . -B "build32"
    cmake -G "Visual Studio 16 2019" -A x64 -S . -B "build64"
    cmake --build build32 --config Release --target install
    cmake --build build64 --config Release --target install
     ;;

   # Add here more strings to compare
   # See correspondence table at the bottom of this answer

   *)
    cmake -S . -B "build" -DCMAKE_OSX_ARCHITECTURES="arm64;x86_64"
    cmake --build build --config Release --target install 
     ;;
esac




