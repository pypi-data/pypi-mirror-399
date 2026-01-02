#ifndef DIHEDRALTENSORGROUPIMP
#define DIHEDRALTENSORGROUPIMP

#include "dihedral_matrix.hpp"

static void dihedral_matrix_dealloc(dihedral_matrix *self)
{
    if(self->r)
    Py_DECREF(self->r);
    if(self->s)
    Py_DECREF(self->s);
    Py_TYPE(self)->tp_free((PyObject*)self);
}

static PyObject * dihedral_matrix_str(dihedral_matrix *self){
    PyObject *s_str = PyObject_Str((PyObject*) self->s);
    if (!s_str) return NULL;

    PyObject *r_str = PyObject_Str((PyObject*) self->r);
    if (!r_str) { Py_DECREF(r_str); return NULL; }


    PyObject* out = PyUnicode_FromFormat(
        "Dihedral Tensor:\n"
        "Sides: %zd\n"
        "Power of S: \n%U\n"
        "Power of R: \n%U",
        (Py_ssize_t)self->n,
        s_str,
        r_str
    );

    Py_DECREF(s_str);
    Py_DECREF(r_str);
    return out;
}

static PyObject * dihedral_matrix_new(PyTypeObject *type, PyObject *args, PyObject *kwds){
    (void)args;
    (void)kwds;
    dihedral_matrix *self = (dihedral_matrix*)type->tp_alloc(type, 0);
    self->s = nullptr;
    self->r = nullptr;
    return (PyObject*)self;
}

void modn(void* elem, uint8_t dtype, long val){
    long* e = (long*) elem;
    e[0] %= val;
    if(e[0] < 0){
        e[0] += val;
    }
    return;
}

static int dihedral_matrix_init(dihedral_matrix *self, PyObject *args, PyObject *kwds){
    static char *kwlist[] = { (char*)"r", (char*)"s", (char*)"n", NULL };
    
    PyObject* r;
    PyObject* s;
    long n;
    if (!PyArg_ParseTupleAndKeywords(args, kwds, "OOl", kwlist, &r, &s, &n))
        return -1;



    self->n = n;

    if(!PyObject_TypeCheck(r, &ndarrayType)){
        PyErr_SetString(PyExc_TypeError, "r needs to be a pypearl ndarray.");
        return -1;
    }

    if(!PyObject_TypeCheck(s, &ndarrayType)){
        PyErr_SetString(PyExc_TypeError, "s needs to be a pypearl ndarray.");
        return -1;
    }

    // rotation, reflection
    ndarray* rot = (ndarray*) r;
    ndarray* ref = (ndarray*) s;

    if(rot->nd != ref->nd){
        PyErr_SetString(PyExc_TypeError, "s and r need to have the same number of dimensions.");
        return -1;
    }

    for(size_t i = 0; i < rot->nd; i++){
        if(rot->dims[i] != ref->dims[i]){
            PyErr_SetString(PyExc_TypeError, "s and r need to have the same shape.");
            return -1;
        }
    }

    if(rot->dtype != 0x3 || ref->dtype != 0x3){
        PyErr_SetString(PyExc_TypeError, "s and r need to both be of type int64.");
        return -1;
    }

    self->r = arrayCInitCopy(rot);
    self->s = arrayCInitCopy(ref);

    ndForeachEDL(self->r, &modn, n);
    ndForeachEDL(self->s, &modn, 2);


    return 0;

}

// NOTE DOES NOT COPY OR INCREF S, R
dihedral_matrix* dihedralMatrixCInit(ndarray* r, int64_t n, ndarray* s){
    dihedral_matrix* self = (dihedral_matrix*)dihedral_matrixType.tp_alloc(&dihedral_matrixType, 0);
    self->r = r;
    self->n = n;
    self->s = s;
    return self;
}

void add_long(void* elem, void* other, uint8_t dtype){
    long* e = (long*) elem;
    long* o = (long*) other;
    e[0]+= o[0];
}

void dihedral_add_helper(dihedral_matrix* d1, dihedral_matrix* d2){
    char* r1 = d1->r->data;
    char* r2 = d2->r->data;
    char* s1 = d1->s->data;
    char* s2 = d2->s->data;

    // This was a niche loop so I implemented it here directly

    size_t* cur_idx = (size_t*)malloc(d1->r->nd*sizeof(size_t));
    for(size_t i = 0; i < d1->r->nd; i++) cur_idx[i] = 0;

    for(;;){

        if(((long*)s1)[0]==0){
            ((long*)r1)[0]+=((long*)r2)[0];
        }
        else{
            ((long*)r1)[0]+=d1->n-((long*)r2)[0];
        }

        // Assumes that negative entries weren't input, should be impossible as long as other functions are maintained.
        ((long*)r1)[0] %= d1->n;
        
        ((long*)s1)[0] = (((long*)s1)[0]+((long*)s2)[0])%2;

        for(ssize_t k = (ssize_t)d1->r->nd-1; k >=0; k--){
            cur_idx[k]++;
            r1 += d1->r->strides[k];
            r2 += d2->r->strides[k];

            s1 += d1->s->strides[k];
            s2 += d2->s->strides[k];

            if(cur_idx[k] < d1->r->dims[k]){
                goto next_element;
            }
            r1 -= d1->r->strides[k] * d1->r->dims[k];
            r2 -= d2->r->strides[k] * d2->r->dims[k];

            s1 -= d1->s->strides[k] * d1->s->dims[k];
            s2 -= d2->s->strides[k] * d2->s->dims[k];

            cur_idx[k] = 0;
        }
        break;
        next_element:
        ;
    }
    free(cur_idx);
}

static PyObject* PyDihedral_Matrix_add_new(PyObject *a, PyObject *b){
    dihedral_matrix* d1 = (dihedral_matrix*) a;
    dihedral_matrix* d2 = (dihedral_matrix*) b;


    if(d1->n != d2->n){
        PyErr_SetString(PyExc_TypeError, "Cannot add two dihedral tensors from unequal dihedral groups.");
        return NULL;
    }

    if(d1->r->nd != d2->r->nd || d1->s->nd != d2->s->nd){
        PyErr_SetString(PyExc_TypeError, "Cannot add two dihedral tensors of unequal dimensions.");
        return NULL;
    }

    // works for d1 and d2 since prev check makes sure that these values are the same in both
    if(d1->r->nd != d1->s->nd){
        PyErr_SetString(PyExc_TypeError, "THIS ERROR SHOULD NEVER APPEAR. Somehow a dihedral tensor exists such that s and r are not the same shape. If this wasn't intentional, there is a bug elsewhere in the library, please send me your code so I can find it.");
        return NULL;
    }

    for(size_t i = 0; i < d1->r->nd; i++){
        if(d1->r->dims[i] != d2->r->dims[i] || d1->s->dims[i] != d2->s->dims[i]){
            PyErr_SetString(PyExc_TypeError, "Cannot add two dihedral tensors of unequal shapes.");
            return NULL;
        }
        if(d1->r->dims[i] != d1->s->dims[i]){
            PyErr_SetString(PyExc_TypeError, "THIS ERROR SHOULD NEVER APPEAR. Somehow a dihedral tensor exists such that s and r are not the same shape. If this wasn't intentional, there is a bug elsewhere in the library, please send me your code so I can find it. If it was still send it if you're nice.");
            return NULL;
        }
    }

    ndarray* new_r = arrayCInitCopy(d1->r);
    ndarray* new_s = arrayCInitCopy(d1->s);

    dihedral_matrix* self = dihedralMatrixCInit(new_r, d1->n, new_s);

    dihedral_add_helper(self, d2);

    return (PyObject*) self;
}

static PyObject* PyDihedral_Matrix_add(PyObject *a, PyObject *b){
    dihedral_matrix* d1 = (dihedral_matrix*) a;
    dihedral_matrix* d2 = (dihedral_matrix*) b;


    if(d1->n != d2->n){
        PyErr_SetString(PyExc_TypeError, "Cannot add two dihedral tensors from unequal dihedral groups.");
        return NULL;
    }

    if(d1->r->nd != d2->r->nd || d1->s->nd != d2->s->nd){
        PyErr_SetString(PyExc_TypeError, "Cannot add two dihedral tensors of unequal dimensions.");
        return NULL;
    }

    // works for d1 and d2 since prev check makes sure that these values are the same in both
    if(d1->r->nd != d1->s->nd){
        PyErr_SetString(PyExc_TypeError, "THIS ERROR SHOULD NEVER APPEAR. Somehow a dihedral tensor exists such that s and r are not the same shape. If this wasn't intentional, there is a bug elsewhere in the library, please send me your code so I can find it.");
        return NULL;
    }

    for(size_t i = 0; i < d1->r->nd; i++){
        if(d1->r->dims[i] != d2->r->dims[i] || d1->s->dims[i] != d2->s->dims[i]){
            PyErr_SetString(PyExc_TypeError, "Cannot add two dihedral tensors of unequal shapes.");
            return NULL;
        }
        if(d1->r->dims[i] != d1->s->dims[i]){
            PyErr_SetString(PyExc_TypeError, "THIS ERROR SHOULD NEVER APPEAR. Somehow a dihedral tensor exists such that s and r are not the same shape. If this wasn't intentional, there is a bug elsewhere in the library, please send me your code so I can find it. If it was still send it if you're nice.");
            return NULL;
        }
    }

    dihedral_add_helper(d1, d2);

    Py_INCREF(d1);
    return (PyObject*) d1;
}


static PyObject* PyDihedral_Matrix_richcompare(PyObject* a, PyObject* b, int op)
{
    dihedral_matrix* d1 = (dihedral_matrix*) a;
    dihedral_matrix* d2 = (dihedral_matrix*) b;

    if (op != Py_EQ && op != Py_NE) {
        PyErr_SetString(PyExc_TypeError, "What does inequality even mean in a dihedral group?? Like actually email me.");
        Py_RETURN_NOTIMPLEMENTED;
    }
    bool r_eq = PyNDArray_equal(d1->r, d2->r);
    bool s_eq = PyNDArray_equal(d1->s, d2->s);

    int eq = (d1->n == d2->n) && r_eq && s_eq;

    switch(op){
        case Py_EQ:
        return PyBool_FromLong(eq);
        break;
        case Py_NE:
        return PyBool_FromLong(!eq);
        break;
    }
}

PyMethodDef dihedral_matrix_methods[] = {
    /*{"div", (PyCFunction)PyNDArray_div, METH_O, "divides a number from an array"},*/
    {NULL, NULL, 0, NULL}
};

static PyMemberDef PyDihedral_matrix_members[] = {
    {"n", T_LONG, offsetof(dihedral_matrix, n), READONLY, "group order parameter n"},
    {"s", T_OBJECT_EX, offsetof(dihedral_matrix, s), READONLY, "exponent tensor of s (0 or 1)"},
    {"r", T_OBJECT_EX, offsetof(dihedral_matrix, r), READONLY, "exponent tensor of r (0..n-1)"},
    {NULL}
};

static PyNumberMethods dihedral_matrix_as_number = {
    /* nb_add */                  PyDihedral_Matrix_add_new,        // a + b
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

    /* nb_inplace_add */          PyDihedral_Matrix_add,       // a += b
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

PyTypeObject dihedral_matrixType = {
    PyVarObject_HEAD_INIT(NULL, 0)
    "pypearl.DihedralTensor",               // tp_name
    sizeof(dihedral_matrix),         // tp_basicsize
    0,                               // tp_itemsize
    (destructor)dihedral_matrix_dealloc,   // tp_dealloc
    0,                               // tp_vectorcall_offset / tp_print
    0,                               // tp_getattr
    0,                               // tp_setattr
    0,                               // tp_reserved / tp_compare
    (reprfunc)dihedral_matrix_str,         // tp_repr
    &dihedral_matrix_as_number,              // tp_as_number
    0,                               // tp_as_sequence
    0,                               // tp_as_mapping
    0,                               // tp_hash
    0,                               // tp_call
    (reprfunc)dihedral_matrix_str,         // tp_str
    0,                               // tp_getattro
    0,                               // tp_setattro
    0,                               // tp_as_buffer
    Py_TPFLAGS_DEFAULT,              // tp_flags
    "Dihedral Tensor Element of format sr^{n}",              // tp_doc
    0,                               // tp_traverse
    0,                               // tp_clear
    PyDihedral_Matrix_richcompare,                               // tp_richcompare
    0,                               // tp_weaklistoffset
    0,                               // tp_iter
    0,                               // tp_iternext
    dihedral_matrix_methods,               // tp_methods
    PyDihedral_matrix_members,                               // tp_members
    0,                // tp_getset
    0,                               // tp_base
    0,                               // tp_dict
    0,                               // tp_descr_get
    0,                               // tp_descr_set
    0,                               // tp_dictoffset
    (initproc)dihedral_matrix_init,        // tp_init
    0,                               // tp_alloc
    dihedral_matrix_new                    // tp_new
};

#endif