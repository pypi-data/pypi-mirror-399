#ifndef SYMGROUP
#define SYMGROUP

// Symmetric Groups

#include <Python.h> 
#include <structmember.h> 
#include "../../matrix/structures/ndarray.hpp"

typedef struct {
    PyObject_HEAD
    
    // Saved in notation of the new ordering, rather than as a product of cycles, transpositions, etc. Always 1D.
    ndarray* ordering;
    
    // S_n. Should always equal orderings->dims[0], kept on struct for convenience.
    int64_t n;
    
} symmetric;

// Python handling
static void symmetric_dealloc(symmetric *self);
static PyObject * symmetric_str(symmetric *self);
static PyObject * symmetric_new(PyTypeObject *type, PyObject *args, PyObject *kwds);
static int symmetric_init(symmetric *self, PyObject *args, PyObject *kwds);
extern PyMethodDef symmetric_methods[];
extern PyTypeObject symmetricType;

// Methods
symmetric* symmetricCInit(ndarray* order, uint64_t n);
static PyObject* PySymmetric_add_new(PyObject *Pyself, PyObject *arg);

#include "symmetric.cpp"

#endif