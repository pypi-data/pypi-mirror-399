#ifndef DIHEDRALTENSORGROUP
#define DIHEDRALTENSORGROUP

#include <Python.h> 
#include <structmember.h> 

#include "dihedral.hpp"
#include "../../python_utility/volume1.hpp"
#include "../../matrix/structures/ndarray.hpp"

typedef struct {
    PyObject_HEAD
    
    // Sign
    ndarray* s;
    
    // Rotations
    ndarray* r;

    int64_t n;
    
} dihedral_matrix;

// Python handling
static void dihedral_matrix_dealloc(dihedral_matrix *self);
static PyObject * dihedral_matrix_str(dihedral_matrix *self);
static PyObject * dihedral_matrix_new(PyTypeObject *type, PyObject *args, PyObject *kwds);
static int dihedral_matrix_init(dihedral_matrix *self, PyObject *args, PyObject *kwds);
extern PyMethodDef dihedral_matrix_methods[];
extern PyTypeObject dihedral_matrixType;

// Methods
dihedral_matrix* dihedralMatrixCInit(ndarray* r, int64_t n, ndarray* s);
static PyObject* PyDihedral_Matrix_add_new(PyObject *a, PyObject *b);

#include "dihedral_matrix.cpp"

#endif