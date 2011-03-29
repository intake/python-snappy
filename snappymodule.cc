/*
    python bindings for the snappy compression library from Google (c)
    Copyright (C) 2011  Andres Moreira

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
*/
#include <Python.h>
#include <string.h>
#include <stdio.h>

#ifdef __cplusplus
#include <string>
#include <snappy.h>
    
using namespace std;

/*
 * snappy max_compressed_size
 *
 * Returns the max compressed size given the length of the
 * character buffer to compress
 */
extern "C" size_t snappy_max_compressed_size(size_t length) {
    return snappy::MaxCompressedLength(length);
}

/*
 * snappy get_uncompressed_length
 *
 * Returns the length of the uncompressed character buffer
 */
extern "C" int snappy_get_uncompressed_length(const char* compressed, 
    size_t compressed_length, size_t* result) {
    return (int)snappy::GetUncompressedLength(compressed, compressed_length, 
        result);
}

/*
 * snappy is_valid_compressed_buffer binding
 *
 *  Returns True if the given compressed buffer is a valid one, False 
 *  in other case
 */
extern "C" int snappy_is_valid_compressed_buffer(const char* compressed, 
    size_t compressed_length) {
    return (int)snappy::IsValidCompressedBuffer(compressed, compressed_length);
}

/*
 * snappy compress C binding
 *
 * Compress input and place the result in "output"
 * Returns the length of the character buffer compressed
 */
extern "C" size_t snappy_compress(const char * input, size_t input_size, char * output) 
{
    string sout;
    size_t ncompbytes;

    ncompbytes = snappy::Compress(input, input_size, &sout);
    memcpy(output, sout.data(), ncompbytes);
    return ncompbytes;
}

/*
 * snappy uncompress C binding
 * 
 * Returns :
 *  - 0 if there is an error while uncompressing or getting the uncompressed
 *    length.
 *  - length(uncompressed string) in other case
 */
extern "C" int snappy_uncompress(const char * compr, size_t compressed_length, 
    char * output) 
{
    string uncompressed;
    size_t uncomp_size;
    bool result;
    
    result = snappy::Uncompress(compr, compressed_length, &uncompressed);
    if (!result)
        return 0;

    result = snappy_get_uncompressed_length(compr, compressed_length, &uncomp_size);
    if (!result)
        return 0;

    memcpy(output, uncompressed.data(), uncomp_size);

    return uncomp_size;
}
#endif


static PyObject *SnappyCompressError,
    *SnappyUncompressError,
    *SnappyInvalidCompressedInputError,
    *SnappyCompressedLengthError;

static PyObject *
snappy__compress(PyObject *self, PyObject *args)
{
    const char * input;
    int input_size;
    char *compressed;
    size_t max_comp_size, real_size;
    PyObject * result;

    if (!PyArg_ParseTuple(args, "s#", &input, &input_size))
        return NULL;

    // Ask for the max size of the compressed object.
    max_comp_size = snappy_max_compressed_size(input_size);

    // Make snappy compression
    compressed = (char*) malloc(sizeof(char) * max_comp_size);
    real_size = snappy_compress(input, input_size, compressed);

    if (real_size > 0) {
        result = Py_BuildValue("s#", compressed, real_size);
        free(compressed);
        return result;
    }

    PyErr_SetString(SnappyCompressError, 
        "Error ocurred while compressing string");
    free(compressed);
    return NULL;
}

static PyObject *
snappy__uncompress(PyObject *self, PyObject *args)
{
    const char * compressed;
    int status, comp_size;
    size_t uncomp_size;
    PyObject * result;

    if (!PyArg_ParseTuple(args, "s#", &compressed, &comp_size))
        return NULL;

    status = snappy_get_uncompressed_length(compressed, comp_size, 
        &uncomp_size);
    if (!status) {
        PyErr_SetString(SnappyCompressedLengthError, 
            "Can not calculate uncompressed length");
        return NULL;
    }

    char * uncompressed = (char *) malloc(sizeof(char) * uncomp_size);
    status = snappy_uncompress(compressed, comp_size, uncompressed);
    if (status != 0) {
        result = Py_BuildValue("s#", uncompressed, uncomp_size);
        free(uncompressed);
        return result;
    }

    free(uncompressed);
    PyErr_SetString(SnappyUncompressError, 
        "An error ocurred while uncompressing the string");
    return NULL;
}


static PyObject *
snappy__is_valid_compressed_buffer(PyObject *self, PyObject *args)
{
    const char * compressed;
    int result, comp_size;

    if (!PyArg_ParseTuple(args, "s#", &compressed, &comp_size))
        return NULL;

    result = snappy_is_valid_compressed_buffer(compressed, comp_size);
    if (result)
        Py_RETURN_TRUE;
    Py_RETURN_FALSE;
}


static PyMethodDef snappy_methods[] = {
    {"compress",  snappy__compress, METH_VARARGS, 
        "Compress a string using the snappy library."},
    {"uncompress",  snappy__uncompress, METH_VARARGS, 
        "Uncompress a string compressed with the snappy library."},
    {"isValidCompressed",  snappy__is_valid_compressed_buffer, METH_VARARGS, 
        "Returns True if the compressed buffer is valid, False otherwise"},
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

    SnappyCompressError = PyErr_NewException((char*)"snappy.CompressError", 
        NULL, NULL);
    SnappyUncompressError = PyErr_NewException((char*)"snappy.UncompressError",
        NULL, NULL);
    SnappyInvalidCompressedInputError = PyErr_NewException(
        (char*)"snappy.InvalidCompressedInputError", NULL, NULL);
    SnappyCompressedLengthError = PyErr_NewException(
        (char*)"snappy.CompressedLengthError", NULL, NULL);

    Py_INCREF(SnappyCompressError);
    Py_INCREF(SnappyUncompressError);
    Py_INCREF(SnappyInvalidCompressedInputError);
    Py_INCREF(SnappyCompressedLengthError);

    PyModule_AddObject(m, "CompressError", SnappyCompressError);
    PyModule_AddObject(m, "UncompressError", SnappyUncompressError);
    PyModule_AddObject(m, "InvalidCompressedInputError", 
        SnappyInvalidCompressedInputError);
    PyModule_AddObject(m, "CompressedLengthError", SnappyCompressedLengthError);
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
