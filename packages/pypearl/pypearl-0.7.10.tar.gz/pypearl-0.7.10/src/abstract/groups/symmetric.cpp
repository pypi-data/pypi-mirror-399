#ifndef SYMGROUPIMP
#define SYMGROUPIMP

#include "symmetric.hpp"

static void symmetric_dealloc(symmetric *self)
{
    if(self->ordering)
    Py_DECREF(self->ordering);
    Py_TYPE(self)->tp_free((PyObject*)self);
}

static PyObject * symmetric_str(symmetric *self){
    PyObject *o_str = PyObject_Str((PyObject*) self->ordering);
    if (!o_str) { Py_DECREF(o_str); return NULL; }


    PyObject* str = PyUnicode_FromFormat(
        "Symmetric Element:\n"
        "Order: %zd\n"
        "In the Cyclic Group Order: \n%U",
        (Py_ssize_t)self->n,
        o_str
    );
    Py_DECREF(o_str);
    return str;
}

static PyObject * symmetric_new(PyTypeObject *type, PyObject *args, PyObject *kwds){
    (void)args;
    (void)kwds;
    symmetric* self = (symmetric*)type->tp_alloc(type, 0);
    self->ordering=nullptr;
    self->n=0;
    return (PyObject*)self;
}

static int symmetric_init(symmetric *self, PyObject *args, PyObject *kwds){
    static char *kwlist[] = { (char*)"ordering", (char*)"n", NULL };
    
    PyObject* val = nullptr;
    long n = 0;
    if (!PyArg_ParseTupleAndKeywords(args, kwds, "|Ol", kwlist, &val, &n))
        return -1;

    if(!val){
        if(n){
            self->n = n;
            if(n < 0){
                PyErr_SetString(PyExc_TypeError, "Symmetric group is only defined for possible lengths of sets (n must be positive).");
                return -1;
            }
            size_t len = (size_t)n;
            ndarray* arr = arrayCInit(0x1, 0x3, &len);
            for(size_t i = 0; i < len; i++){
                fastSet1D8Index(arr, i, &i);
            }
            self->ordering = arr;
            return 0;
        }
        else{
            PyErr_SetString(PyExc_TypeError, "Must pass either n or ordering.");
            return -1;
        }
    }
    if(!PyObject_TypeCheck(val, &ndarrayType)){
        PyErr_SetString(PyExc_TypeError, "ordering must be an ndarray from the pypearl library.");
        return -1;
    }
    if(((ndarray*)val)->dtype != 0x3){
        PyErr_SetString(PyExc_TypeError, "use int64 for symmetric group.");
        return -1;
    }
    ndarray* arr = arrayCInitCopy((ndarray*) val);

    self->n = arr->dims[0];
    self->ordering = arr;

    return 0;
}


// ORDER IS USED DIRECTLY NOT COPIED
symmetric* symmetricCInit(ndarray* order, int64_t n){
    symmetric* self = (symmetric*)symmetricType.tp_alloc(&symmetricType, 0);
    self->n = n;
    self->ordering = order;
    return self;
}

void symmetric_add_helper(symmetric* a, symmetric* b){
    long temp[a->n];
    // I see a bug of long and size_t being different, but most machines have 64 bit size_t, meaning you'd need to allocate an array millions of terabytes big. There's definitely like 1 specific machine where is some crazy glitch or something.
    for(long i = 0; i < a->n; i++){
        long index;
        long index2;
        fastGet1D8Index(b->ordering, i, &index);
        fastGet1D8Index(a->ordering, index, &index2);
        temp[i] = index2;
    }
    for(long i =0; i < a->n; i++){
        long x = temp[i];
        fastSet1D8Index(a->ordering, i, &x);
    }
}

static PyObject* PySymmetric_add_new(PyObject *a, PyObject *b){
    if(!PyObject_TypeCheck(a, &symmetricType)){
        PyErr_SetString(PyExc_TypeError, "a must be a symmetric group element");
        return NULL;
    }

    if(!PyObject_TypeCheck(b, &symmetricType)){
        PyErr_SetString(PyExc_TypeError, "b must be a symmetric group element");
        return NULL;
    }


    symmetric* s1 = (symmetric*) a;
    symmetric* s2 = (symmetric*) b;


    if(s1->n != s2->n){
        PyErr_SetString(PyExc_TypeError, "Cannot add two elements from symmetric groups of different length.");
        return NULL;
    }

    ndarray* new_order = arrayCInitCopy(s1->ordering);
    symmetric* c = symmetricCInit(new_order, s1->n);

    symmetric_add_helper(c, s2);

    return (PyObject*) c;
}

static PyObject* PySymmetric_add(PyObject *a, PyObject *b){
    if(!PyObject_TypeCheck(a, &symmetricType)){
        PyErr_SetString(PyExc_TypeError, "a must be a symmetric group element");
        return NULL;
    }

    if(!PyObject_TypeCheck(b, &symmetricType)){
        PyErr_SetString(PyExc_TypeError, "b must be a symmetric group element");
        return NULL;
    }

    symmetric* s1 = (symmetric*) a;
    symmetric* s2 = (symmetric*) b;


    if(s1->n != s2->n){
        PyErr_SetString(PyExc_TypeError, "Cannot add two elements from cyclic groups of unequal order.");
        return NULL;
    }

    symmetric_add_helper(s1, s2);

    Py_INCREF(s1);
    return (PyObject*) s1;
}


static PyObject* PySymmetric_richcompare(PyObject* a, PyObject* b, int op)
{
    if(!PyObject_TypeCheck(a, &symmetricType)){
        PyErr_SetString(PyExc_TypeError, "a must be a symmetric group element");
        return NULL;
    }

    if(!PyObject_TypeCheck(b, &symmetricType)){
        PyErr_SetString(PyExc_TypeError, "b must be a symmetric group element");
        return NULL;
    }

    symmetric* s1 = (symmetric*) a;
    symmetric* s2 = (symmetric*) b;

    if (op != Py_EQ && op != Py_NE) {
        PyErr_SetString(PyExc_TypeError, "It is hard to create a well defined inequality for the classes of Z/nZ.");
        Py_RETURN_NOTIMPLEMENTED;
    }

    bool arr_eq = PyNDArray_equal(s1->ordering, s2->ordering);
    int eq = (s1->n == s2->n) && arr_eq;

    switch(op){
        case Py_EQ:
        return PyBool_FromLong(eq);
        break;
        case Py_NE:
        return PyBool_FromLong(!eq);
        break;
    }
}

PyMethodDef symmetric_methods[] = {
    /*{"div", (PyCFunction)PyNDArray_div, METH_O, "divides a number from an array"},*/
    {NULL, NULL, 0, NULL}
};

static PyMemberDef PySymmetric_members[] = {
    {"n", T_LONG, offsetof(symmetric, n), READONLY, "group order n"},
    {"ordering", T_OBJECT_EX, offsetof(symmetric, ordering), READONLY,"array of reordering"},
    {NULL}
};

static PyNumberMethods symmetric_as_number = {
    /* nb_add */                  PySymmetric_add_new,        // a + b
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

    /* nb_inplace_add */          PySymmetric_add,       // a += b
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

PyTypeObject symmetricType = {
    PyVarObject_HEAD_INIT(NULL, 0)
    "pypearl.Symmetric",               // tp_name
    sizeof(symmetric),         // tp_basicsize
    0,                               // tp_itemsize
    (destructor)symmetric_dealloc,   // tp_dealloc
    0,                               // tp_vectorcall_offset / tp_print
    0,                               // tp_getattr
    0,                               // tp_setattr
    0,                               // tp_reserved / tp_compare
    (reprfunc)symmetric_str,         // tp_repr
    &symmetric_as_number,              // tp_as_number
    0,                               // tp_as_sequence
    0,                               // tp_as_mapping
    0,                               // tp_hash
    0,                               // tp_call
    (reprfunc)symmetric_str,         // tp_str
    0,                               // tp_getattro
    0,                               // tp_setattro
    0,                               // tp_as_buffer
    Py_TPFLAGS_DEFAULT,              // tp_flags
    "Symmetric Group Element",              // tp_doc
    0,                               // tp_traverse
    0,                               // tp_clear
    PySymmetric_richcompare,                               // tp_richcompare
    0,                               // tp_weaklistoffset
    0,                               // tp_iter
    0,                               // tp_iternext
    symmetric_methods,               // tp_methods
    PySymmetric_members,                               // tp_members
    0,                // tp_getset
    0,                               // tp_base
    0,                               // tp_dict
    0,                               // tp_descr_get
    0,                               // tp_descr_set
    0,                               // tp_dictoffset
    (initproc)symmetric_init,        // tp_init
    0,                               // tp_alloc
    symmetric_new                    // tp_new
};

#endif