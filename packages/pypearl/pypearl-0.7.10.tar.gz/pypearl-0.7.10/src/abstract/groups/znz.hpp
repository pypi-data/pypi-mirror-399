#ifndef ZNZGROUP
#define ZNZGROUP

// Cyclic Groups of Order n

#include <Python.h> 
#include <structmember.h> 
#include "../../matrix/structures/ndarray.hpp"

typedef struct {
    PyObject_HEAD
    
    // Representative
    int64_t val;
    
    // Order
    int64_t n;
    
} znz;

// Python handling
static void znz_dealloc(znz *self);
static PyObject * znz_str(znz *self);
static PyObject * znz_new(PyTypeObject *type, PyObject *args, PyObject *kwds);
static int znz_init(znz *self, PyObject *args, PyObject *kwds);
extern PyMethodDef znz_methods[];
extern PyTypeObject znzType;

// Methods
znz* znzCInit(int64_t val, int64_t n);
static PyObject* Pyznz_add_new(PyObject *Pyself, PyObject *arg);

#include "znz.cpp"

#endif