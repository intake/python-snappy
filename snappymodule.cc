#include <Python.h>
#include <string.h>

#ifdef __cplusplus
#include <string>
#include <snappy.h>
    
using namespace std;

extern "C" size_t snappy_max_compressed_size(size_t length) {
    return snappy::MaxCompressedLength(length);
}

extern "C" int snappy_get_uncompressed_length(const char* compressed, 
    size_t compressed_length, size_t* result) {
    return (int)snappy::GetUncompressedLength(compressed, compressed_length, result);
}

extern "C" int snappy_is_valid_compressed_buffer(const char* compressed, 
    size_t compressed_length) {
    return (int)snappy::IsValidCompressedBuffer(compressed, compressed_length);
}

extern "C" size_t snappy_compress(const char * input, char * output) 
{
    string sinp = string(input), 
           sout;
    size_t ncompbytes;

    ncompbytes = snappy::Compress(sinp.data(), sinp.size(), &sout);
    sout.copy(output, sout.size(), 0);

    return ncompbytes;
}

extern "C" int snappy_uncompress(const char * compr, size_t compressed_length, char * output) 
{
    string uncompressed;
    bool result;
    
    result = snappy::Uncompress(compr, compressed_length, &uncompressed);
    uncompressed.copy(output, uncompressed.size(), 0);

    return (int)result;
}
#endif


static PyObject *SnappyError;

static PyObject *
snappy__compress(PyObject *self, PyObject *args)
{
    const char * input;
    char * output, *compressed;
    size_t max_comp_size, real_size;

    if (!PyArg_ParseTuple(args, "s", &input))
        return NULL;

    // Ask for the max size of the compressed object.
    max_comp_size = snappy_max_compressed_size(strlen(input));

    compressed = (char*) malloc(sizeof(char) * max_comp_size);

    // Make snappy compression
    real_size = snappy_compress(input, compressed);

    output = (char*) malloc(sizeof(char) * real_size);
    memcpy(output, compressed, real_size);
    free(compressed);

    if (real_size > 0) 
        return Py_BuildValue("s#", output, real_size);

    PyErr_SetString(SnappyError, "compress: error ocurred while compressing string");
    free(output);
    return NULL;
}

static PyObject *
snappy__uncompress(PyObject *self, PyObject *args)
{
    const char * compressed;
    int status, comp_size;
    size_t uncomp_size;

    if (!PyArg_ParseTuple(args, "s#", &compressed, &comp_size))
        return NULL;

    if (!snappy_is_valid_compressed_buffer(compressed, comp_size)) {
        PyErr_SetString(SnappyError, "uncompress: given compressed string is not valid!");
        return NULL;
    }

    status = snappy_get_uncompressed_length(compressed, comp_size, &uncomp_size);
    if (!status) {
        PyErr_SetString(SnappyError, "uncompress: can not calculate uncompressed length");
        return NULL;
    }

    char * uncompressed = (char *) malloc(sizeof(char) * uncomp_size);
    status = snappy_uncompress(compressed, comp_size, uncompressed);
    if (status > 0)
        return Py_BuildValue("s#", uncompressed, uncomp_size);

    PyErr_SetString(SnappyError, "An error ocurred while uncompressing string");
    return NULL;
}

static PyMethodDef snappy_methods[] = {
    {"compress",  snappy__compress, METH_VARARGS, "Compress a string using the snappy library."},
    {"uncompress",  snappy__uncompress, METH_VARARGS, "Uncompress a string compressed with the snappy library."},
    {NULL, NULL, 0, NULL}        /* Sentinel */
};

#ifndef PyMODINIT_FUNC
#define PyMODINIT_FUNC void
#endif

PyMODINIT_FUNC
initsnappy(void)
{
    PyObject *m;

    PyImport_AddModule("snappy");
    m = Py_InitModule("snappy", snappy_methods);
    if (m == NULL)
        return;

    SnappyError = PyErr_NewException((char*)"snappy.error", NULL, NULL);
    Py_INCREF(SnappyError);
    PyModule_AddObject(m, "error", SnappyError);
}


int main(int argc, char **argv)
{
    /* Pass argv[0] to the Python interpreter */
    Py_SetProgramName(argv[0]);

    /* Initialize the Python interpreter.  Required. */
    Py_Initialize();

    /* Add a static module */
    initsnappy();

    /* Exit, cleaning up the interpreter */
    Py_Exit(0);
    return 0;
}
