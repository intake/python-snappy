/*
Copyright (c) 2011, Andres Moreira <andres@andresmoreira.com>
              2011, Felipe Cruz <felipecruz@loogica.net>
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:
    * Redistributions of source code must retain the above copyright
      notice, this list of conditions and the following disclaimer.
    * Redistributions in binary form must reproduce the above copyright
      notice, this list of conditions and the following disclaimer in the
      documentation and/or other materials provided with the distribution.
    * Neither the name of the authors nor the
      names of its contributors may be used to endorse or promote products
      derived from this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL ANDRES MOREIRA BE LIABLE FOR ANY
DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
(INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
*/
#include "Python.h"
#include <string.h>
#include <stdio.h>
#include <snappy-c.h>

struct module_state {
    PyObject *error;
};

#if PY_MAJOR_VERSION >= 3
#define GETSTATE(m) ((struct module_state*)PyModule_GetState(m))
#else
#define GETSTATE(m) (&_state)
static struct module_state _state;
#endif


static PyObject *SnappyCompressError,
    *SnappyUncompressError,
    *SnappyInvalidCompressedInputError,
    *SnappyCompressedLengthError;

static PyObject *
snappy__compress(PyObject *self, PyObject *args)
{
#if PY_MAJOR_VERSION >= 3
    Py_buffer pbuffer;
#endif
    const char * input;
    int input_size;
    char *compressed;
    size_t max_comp_size, real_size;
    PyObject * result;

    snappy_status status;

#if PY_MAJOR_VERSION >= 3
    if (!PyArg_ParseTuple(args, "y#", &pbuffer, &input_size))
#else
    if (!PyArg_ParseTuple(args, "s#", &input, &input_size))
#endif
        return NULL;

#if PY_MAJOR_VERSION >= 3
    input = (char*)pbuffer.buf;
#endif
    // Ask for the max size of the compressed object.
    max_comp_size = snappy_max_compressed_length(input_size);

    // Make snappy compression
    compressed = (char*) malloc(sizeof(char) * max_comp_size);
    status = snappy_compress(input, input_size, compressed, &real_size);

    if (status == SNAPPY_OK) {
#if PY_MAJOR_VERSION >= 3
        result = PyBytes_FromStringAndSize((char *)compressed, real_size);
#else
        result = Py_BuildValue("s#", compressed, real_size);
#endif
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
 #if PY_MAJOR_VERSION >= 3
    Py_buffer pbuffer;
#endif   
    const char * compressed;
    int comp_size;
    size_t uncomp_size;
    PyObject * result;
    snappy_status status;

#if PY_MAJOR_VERSION >=3
    if (!PyArg_ParseTuple(args, "y#", &pbuffer, &comp_size))
#else
    if (!PyArg_ParseTuple(args, "s#", &compressed, &comp_size))
#endif
        return NULL;

#if PY_MAJOR_VERSION >= 3
    compressed = (char*) pbuffer.buf;
#endif
    
    status = snappy_uncompressed_length(compressed, comp_size, 
        &uncomp_size);
    if (status != SNAPPY_OK) {
        PyErr_SetString(SnappyCompressedLengthError, 
            "Can not calculate uncompressed length");
        return NULL;
    }

    char * uncompressed = (char *) malloc(sizeof(char) * uncomp_size);
    status = snappy_uncompress(compressed, comp_size, uncompressed, &uncomp_size);
    if (status == SNAPPY_OK) {
#if PY_MAJOR_VERSION >= 3
        result = PyBytes_FromStringAndSize((char *)uncompressed, uncomp_size);
#else
        result = Py_BuildValue("s#", uncompressed, uncomp_size);
#endif
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
    int comp_size;
    snappy_status status;

    if (!PyArg_ParseTuple(args, "s#", &compressed, &comp_size))
        return NULL;

    status = snappy_validate_compressed_buffer(compressed, comp_size);
    if (status == SNAPPY_OK)
        Py_RETURN_TRUE;
    Py_RETURN_FALSE;
}

static PyMethodDef snappy_methods[] = {
    {"compress",  snappy__compress, METH_VARARGS, 
        "Compress a string using the snappy library."},
    {"uncompress",  snappy__uncompress, METH_VARARGS, 
        "Uncompress a string compressed with the snappy library."},
    {"decompress",  snappy__uncompress, METH_VARARGS, 
        "Alias to Uncompress method, to be compatible with zlib."},
    {"isValidCompressed",  snappy__is_valid_compressed_buffer, METH_VARARGS, 
        "Returns True if the compressed buffer is valid, False otherwise"},
    {NULL, NULL, 0, NULL}        /* Sentinel */
};

#if PY_MAJOR_VERSION >= 3

static int snappy_traverse(PyObject *m, visitproc visit, void *arg) {
    Py_VISIT(GETSTATE(m)->error);
    return 0;
}

static int snappy_clear(PyObject *m) {
    Py_CLEAR(GETSTATE(m)->error);
    return 0;
}


static struct PyModuleDef moduledef = {
        PyModuleDef_HEAD_INIT,
        "snappy",
        NULL,
        sizeof(struct module_state),
        snappy_methods,
        NULL,
        snappy_traverse,
        snappy_clear,
        NULL
};


#define INITERROR return NULL

PyMODINIT_FUNC
PyInit_snappy(void)

#else
#define INITERROR return

PyMODINIT_FUNC
initsnappy(void)
#endif
{
    PyObject *m;

    #if PY_MAJOR_VERSION >= 3
    m = PyModule_Create(&moduledef);
    #else
    m = Py_InitModule("snappy", snappy_methods);
    #endif

    if (m == NULL)
        INITERROR;

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

#if PY_MAJOR_VERSION >= 3
    return m;
#endif
}

