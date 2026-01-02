#ifndef ZNZGROUPIMP
#define ZNZGROUPIMP

#include "znz.hpp"

static void znz_dealloc(znz *self)
{

    Py_TYPE(self)->tp_free((PyObject*)self);
}

static PyObject * znz_str(znz *self){

    return PyUnicode_FromFormat(
        "Cyclic Element:\n"
        "Representative: %zd\n"
        "In the Cyclic Group Order: %zd\n",
        (Py_ssize_t)self->val,
        (Py_ssize_t)self->n
    );
}

static PyObject * znz_new(PyTypeObject *type, PyObject *args, PyObject *kwds){
    (void)args;
    (void)kwds;
    znz *self = (znz*)type->tp_alloc(type, 0);

    return (PyObject*)self;
}

static int znz_init(znz *self, PyObject *args, PyObject *kwds){
    static char *kwlist[] = { (char*)"rep", (char*)"n", NULL };
    
    long val;
    long n;
    if (!PyArg_ParseTupleAndKeywords(args, kwds, "|ll", kwlist, &val, &n))
        return -1;

    self->n = n;

    self->val = val%n;
    if(self->val < 0){
        self->val += n;
    }

    return 0;
}

znz* znzCInit(int64_t val, int64_t n){
    znz* self = (znz*)znzType.tp_alloc(&znzType, 0);
    self->val = val;
    self->n = n;
    return self;
}

static PyObject* Pyznz_add_new(PyObject *a, PyObject *b){
    znz* z1 = (znz*) a;
    znz* z2 = (znz*) b;


    if(z1->n != z2->n){
        PyErr_SetString(PyExc_TypeError, "Cannot add two elements from cyclic groups of unequal order.");
        return NULL;
    }
    int64_t val = (z1->val + z2->val)%z1->n;



    znz* self = znzCInit(val, z1->n);

    return (PyObject*) self;
}

static PyObject* Pyznz_add(PyObject *a, PyObject *b){
    znz* z1 = (znz*) a;
    znz* z2 = (znz*) b;


    if(z1->n != z2->n){
        PyErr_SetString(PyExc_TypeError, "Cannot add two elements from cyclic groups of unequal order.");
        return NULL;
    }
    z1->val = (z1->val + z2->val)%z1->n;

    Py_INCREF(z1);
    return (PyObject*) z1;
}


static PyObject* Pyznz_richcompare(PyObject* a, PyObject* b, int op)
{
    znz* z1 = (znz*) a;
    znz* z2 = (znz*) b;

    if (op != Py_EQ && op != Py_NE) {
        PyErr_SetString(PyExc_TypeError, "It is hard to create a well defined inequality for the classes of Z/nZ.");
        Py_RETURN_NOTIMPLEMENTED;
    }

    int eq = (z1->n == z2->n) && (z1->val == z2->val);

    switch(op){
        case Py_EQ:
        return PyBool_FromLong(eq);
        break;
        case Py_NE:
        return PyBool_FromLong(!eq);
        break;
    }
}

PyMethodDef znz_methods[] = {
    /*{"div", (PyCFunction)PyNDArray_div, METH_O, "divides a number from an array"},*/
    {NULL, NULL, 0, NULL}
};

static PyMemberDef Pyznz_members[] = {
    {"n", T_LONG, offsetof(znz, n), READONLY, "group order n"},
    {"rep", T_LONG, offsetof(znz, val), READONLY,        "representative between (0...n-1)"},
    {NULL}
};

static PyNumberMethods znz_as_number = {
    /* nb_add */                  Pyznz_add_new,        // a + b
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

    /* nb_inplace_add */          Pyznz_add,       // a += b
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

PyTypeObject znzType = {
    PyVarObject_HEAD_INIT(NULL, 0)
    "pypearl.ZNZ",               // tp_name
    sizeof(znz),         // tp_basicsize
    0,                               // tp_itemsize
    (destructor)znz_dealloc,   // tp_dealloc
    0,                               // tp_vectorcall_offset / tp_print
    0,                               // tp_getattr
    0,                               // tp_setattr
    0,                               // tp_reserved / tp_compare
    (reprfunc)znz_str,         // tp_repr
    &znz_as_number,              // tp_as_number
    0,                               // tp_as_sequence
    0,                               // tp_as_mapping
    0,                               // tp_hash
    0,                               // tp_call
    (reprfunc)znz_str,         // tp_str
    0,                               // tp_getattro
    0,                               // tp_setattro
    0,                               // tp_as_buffer
    Py_TPFLAGS_DEFAULT,              // tp_flags
    "Cyclic Group Order N Element",              // tp_doc
    0,                               // tp_traverse
    0,                               // tp_clear
    Pyznz_richcompare,                               // tp_richcompare
    0,                               // tp_weaklistoffset
    0,                               // tp_iter
    0,                               // tp_iternext
    znz_methods,               // tp_methods
    Pyznz_members,                               // tp_members
    0,                // tp_getset
    0,                               // tp_base
    0,                               // tp_dict
    0,                               // tp_descr_get
    0,                               // tp_descr_set
    0,                               // tp_dictoffset
    (initproc)znz_init,        // tp_init
    0,                               // tp_alloc
    znz_new                    // tp_new
};

#endif