#ifndef DIHEDRALGROUPIMP
#define DIHEDRALGROUPIMP

#include "dihedral.hpp"

static void dihedral_dealloc(dihedral *self)
{    
    Py_TYPE(self)->tp_free((PyObject*)self);
}

static PyObject * dihedral_str(dihedral *self){

    return PyUnicode_FromFormat(
        "Dihedral Element:\n"
        "Sides: %zd\n"
        "Power of S: %zd\n"
        "Power of R: %zd",
        (Py_ssize_t)self->n,
        (Py_ssize_t)self->s,
        (Py_ssize_t)self->r
    );
}

static PyObject * dihedral_new(PyTypeObject *type, PyObject *args, PyObject *kwds){
    (void)args;
    (void)kwds;
    dihedral *self = (dihedral*)type->tp_alloc(type, 0);

    return (PyObject*)self;
}

static int dihedral_init(dihedral *self, PyObject *args, PyObject *kwds){
    static char *kwlist[] = { (char*)"r", (char*)"s", (char*)"n", NULL };
    
    long r;
    long s;
    long n;
    if (!PyArg_ParseTupleAndKeywords(args, kwds, "|lll", kwlist, &r, &s, &n))
        return -1;

    self->n = n;

    self->r = r%n;
    if(self->r < 0){
        self->r += n;
    }
    int64_t temp = s%2;
    if(temp < 0){
        temp *=-1;
    }
    self->s = temp;

    return 0;

}

dihedral* dihedralCInit(int64_t r, int64_t n, int64_t s){
    dihedral* self = (dihedral*)dihedralType.tp_alloc(&dihedralType, 0);
    self->r = r;
    self->n = n;
    self->s = s;
    return self;
}

static PyObject* PyDihedral_add_new(PyObject *Pyself, PyObject *arg){
    dihedral* d1 = (dihedral*) Pyself;
    dihedral* d2 = (dihedral*) arg;


    if(d1->n != d2->n){
        PyErr_SetString(PyExc_TypeError, "Cannot add two dihedral elements from unequal dihedral groups.");
        return NULL;
    }
    int64_t new_r = d1->r;

    //rs
    if(d1->s == 1){
        new_r += d1->n-d2->r;
    }
    else{
        new_r += d2->r;
    }

    new_r %= d1->n;
    int64_t new_s = (d1->s+d2->s)%2;

    dihedral* self = dihedralCInit(new_r, d2->n, new_s);

    return (PyObject*) self;
}

static PyObject* PyDihedral_add(PyObject *Pyself, PyObject *arg){
    dihedral* d1 = (dihedral*) Pyself;
    dihedral* d2 = (dihedral*) arg;


    if(d1->n != d2->n){
        PyErr_SetString(PyExc_TypeError, "Cannot add two dihedral elements from unequal dihedral groups.");
        return NULL;
    }
    int64_t new_r = d1->r;

    //rs
    if(d1->s == 1){
        new_r += d1->n-d2->r;
    }
    else{
        new_r += d2->r;
    }

    new_r %= d1->n;
    int64_t new_s = (d1->s+d2->s)%2;

    d1->s = new_s;
    d1->r = new_r;
    Py_INCREF(d1);
    return (PyObject*) d1;
}


static PyObject* PyDihedral_richcompare(PyObject* a, PyObject* b, int op)
{
    dihedral* d1 = (dihedral*) a;
    dihedral* d2 = (dihedral*) b;

    if (op != Py_EQ && op != Py_NE) {
        PyErr_SetString(PyExc_TypeError, "What does inequality even mean in a dihedral group?? Like actually email me.");
        Py_RETURN_NOTIMPLEMENTED;
    }

    int eq = (d1->n == d2->n) && (d1->s == d2->s) && (d1->r == d2->r);

    switch(op){
        case Py_EQ:
        return PyBool_FromLong(eq);
        break;
        case Py_NE:
        return PyBool_FromLong(!eq);
        break;
    }
}

PyMethodDef dihedral_methods[] = {
    /*{"div", (PyCFunction)PyNDArray_div, METH_O, "divides a number from an array"},*/
    {NULL, NULL, 0, NULL}
};

static PyMemberDef PyDihedral_members[] = {
    {"n", T_LONG, offsetof(dihedral, n), READONLY, "group order parameter n"},
    {"s", T_LONG, offsetof(dihedral, s), READONLY,        "exponent of s (0 or 1)"},
    {"r", T_LONG, offsetof(dihedral, r), READONLY,        "exponent of r (0..n-1)"},
    {NULL}
};

static PyNumberMethods dihedral_as_number = {
    /* nb_add */                  PyDihedral_add_new,        // a + b
    /* nb_subtract */             0,   // a - b
    /* nb_multiply */             0,   // a * b
    /* nb_remainder */            0,                  // a % b
    /* nb_divmod */               0,                  // divmod(a, b)
    /* nb_power */                0,                  // a ** b
    /* nb_negative */             0,   // -a
    /* nb_positive */             0,                  // +a
    /* nb_absolute */             0,                  // abs(a)
    /* nb_bool */                 0,                  // bool(a)
    /* nb_invert */               0,                  // ~a
    /* nb_lshift */               0,                  // a << b
    /* nb_rshift */               0,                  // a >> b
    /* nb_and */                  0,                  // a & b
    /* nb_xor */                  0,                  // a ^ b
    /* nb_or */                   0,                  // a | b
    /* nb_int */                  0,                  // int(a) / __int__
    /* nb_reserved */             0,                  // reserved / legacy
    /* nb_float */                0,                  // float(a) / __float__

    /* nb_inplace_add */          PyDihedral_add,       // a += b
    /* nb_inplace_subtract */     0,       // a -= b
    /* nb_inplace_multiply */     0,       // a *= b
    /* nb_inplace_remainder */    0,                  // a %= b
    /* nb_inplace_power */        0,                  // a **= b
    /* nb_inplace_lshift */       0,                  // a <<= b
    /* nb_inplace_rshift */       0,                  // a >>= b
    /* nb_inplace_and */          0,                  // a &= b
    /* nb_inplace_xor */          0,                  // a ^= b
    /* nb_inplace_or */           0,                  // a |= b

    /* nb_floor_divide */         0,                  // a // b
    /* nb_true_divide */          0,    // a / b
    /* nb_inplace_floor_divide */ 0,                  // a //= b
    /* nb_inplace_true_divide */  0,   // a /= b

    /* nb_index */                0,                  // a.__index__()

    /* nb_matrix_multiply */      0,                  // a @ b
    /* nb_inplace_matrix_multiply */ 0                // a @= b
};

PyTypeObject dihedralType = {
    PyVarObject_HEAD_INIT(NULL, 0)
    "pypearl.Dihedral",               // tp_name
    sizeof(dihedral),         // tp_basicsize
    0,                               // tp_itemsize
    (destructor)dihedral_dealloc,   // tp_dealloc
    0,                               // tp_vectorcall_offset / tp_print
    0,                               // tp_getattr
    0,                               // tp_setattr
    0,                               // tp_reserved / tp_compare
    (reprfunc)dihedral_str,         // tp_repr
    &dihedral_as_number,              // tp_as_number
    0,                               // tp_as_sequence
    0,                               // tp_as_mapping
    0,                               // tp_hash
    0,                               // tp_call
    (reprfunc)dihedral_str,         // tp_str
    0,                               // tp_getattro
    0,                               // tp_setattro
    0,                               // tp_as_buffer
    Py_TPFLAGS_DEFAULT,              // tp_flags
    "Dihedral Element of format sr^{n}",              // tp_doc
    0,                               // tp_traverse
    0,                               // tp_clear
    PyDihedral_richcompare,                               // tp_richcompare
    0,                               // tp_weaklistoffset
    0,                               // tp_iter
    0,                               // tp_iternext
    dihedral_methods,               // tp_methods
    PyDihedral_members,                               // tp_members
    0,                // tp_getset
    0,                               // tp_base
    0,                               // tp_dict
    0,                               // tp_descr_get
    0,                               // tp_descr_set
    0,                               // tp_dictoffset
    (initproc)dihedral_init,        // tp_init
    0,                               // tp_alloc
    dihedral_new                    // tp_new
};

#endif