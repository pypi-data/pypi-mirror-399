#include <Python.h>
#include "matrix/structures/ndarray.hpp"
#include "neuralnetwork/layer/dense.hpp"
#include "./activationbinding/arbitraryactivationbinding.hpp"
//#include "./optimizerbinding/sgdbinding.hpp"
//#include "./modelbinding/modelbinding.hpp"
#include "neuralnetwork/loss/arbitraryloss.hpp"
#include "neuralnetwork/optimizer/arbitraryoptimizer.hpp"
#include "abstract/groups/dihedral.hpp"
#include "abstract/groups/znz.hpp"
#include "abstract/groups/dihedral_matrix.hpp"
#include "abstract/groups/symmetric.hpp"

PyObject* add(PyObject *self, PyObject *args){
    int x;
    int y;  

    PyArg_ParseTuple(args, "ii", &x, &y);

    return PyLong_FromLong(((long)(x+y)));
};   
    
static PyMethodDef methods[] {
    {"add", add, METH_VARARGS, "Adds two numbers together"},
    /*{"breed_models", (PyCFunction)py_breed_models, METH_VARARGS, "breed_models(model1, model2, prop) -> Model"},
    {"copy_model",   (PyCFunction)py_copy_model, METH_O, "copy_model(model) -> Model"},*/
    {NULL, NULL, 0, NULL}
}; 
  
static struct PyModuleDef pypearl = {
    PyModuleDef_HEAD_INIT,
    "pypearl",
    "Documentation: The root of the PyPearl Module.",
    -1,
    methods
};

PyMODINIT_FUNC
PyInit__pypearl(void)
{
    PyObject *m = PyModule_Create(&pypearl);
    if (!m) return NULL;

    // --- register ndarray ---
    if (PyType_Ready(&ndarrayType) < 0) {
        Py_DECREF(m);
        return NULL;
    }
    Py_INCREF(&ndarrayType);
    PyModule_AddObject(m, "ndarray", (PyObject*)&ndarrayType);

    if (PyType_Ready(&denseType) < 0) {
        Py_DECREF(m);
        return NULL;
    }
    Py_INCREF(&denseType);
    PyModule_AddObject(m, "Dense", (PyObject*)&denseType);
    /*
     if (PyType_Ready(&PySGDDType) < 0) {
        Py_DECREF(m); 
        return NULL;
    }
    Py_INCREF(&PySGDDType);
    PyModule_AddObject(m, "SGD", (PyObject*)&PySGDDType);*/

    /*
    if (PyType_Ready(&PyModelType) < 0) {
        Py_DECREF(m); 
        return NULL;
    }
    Py_INCREF(&PyModelType);
    PyModule_AddObject(m, "Model", (PyObject*)&PyModelType);*/


    if (PyType_Ready(&PyALType) < 0) {
        Py_DECREF(m); 
        return NULL;
    }
    Py_INCREF(&PyALType);
    PyModule_AddObject(m, "TestActivation", (PyObject*)&PyALType);

    if (PyType_Ready(&PyRELUType) < 0) {
        Py_DECREF(m); 
        return NULL;
    }
    Py_INCREF(&PyRELUType);
    PyModule_AddObject(m, "ReLU", (PyObject*)&PyRELUType);

    if (PyType_Ready(&PyLinearType) < 0) {
        Py_DECREF(m); 
        return NULL;
    }
    Py_INCREF(&PyLinearType);
    PyModule_AddObject(m, "Linear", (PyObject*)&PyLinearType);

    if (PyType_Ready(&PySigmoidType) < 0) {
        Py_DECREF(m); 
        return NULL;
    }
    Py_INCREF(&PySigmoidType);
    PyModule_AddObject(m, "Sigmoid", (PyObject*)&PySigmoidType);

    if (PyType_Ready(&PyLeakyReLUType) < 0) {
        Py_DECREF(m); 
        return NULL;
    }
    Py_INCREF(&PyLeakyReLUType);
    PyModule_AddObject(m, "LeakyReLU", (PyObject*)&PyLeakyReLUType);

    if (PyType_Ready(&PyStepType) < 0) {
        Py_DECREF(m); 
        return NULL;
    }
    Py_INCREF(&PyStepType);
    PyModule_AddObject(m, "Step", (PyObject*)&PyStepType);


    if (PyType_Ready(&PySoftmaxType) < 0) {
        Py_DECREF(m); 
        return NULL;
    }
    Py_INCREF(&PySoftmaxType);
    PyModule_AddObject(m, "Softmax", (PyObject*)&PySoftmaxType);

    if (PyType_Ready(&PyReverseReLUType) < 0) {
        Py_DECREF(m); 
        return NULL;
    }
    Py_INCREF(&PyReverseReLUType);
    PyModule_AddObject(m, "ReverseReLU", (PyObject*)&PyReverseReLUType);

    if (PyType_Ready(&lossCCEType) < 0) {
        Py_DECREF(m); 
        return NULL;
    }
    Py_INCREF(&lossCCEType);
    PyModule_AddObject(m, "CCE", (PyObject*)&lossCCEType);

    if (PyType_Ready(&optimGDType) < 0) {
        Py_DECREF(m); 
        return NULL;
    }
    Py_INCREF(&optimGDType);
    PyModule_AddObject(m, "GradientDescent", (PyObject*)&optimGDType);

    // Abstract Algebra
    if (PyType_Ready(&dihedralType) < 0) {
        PyErr_Print();  // Print the actual error
        Py_DECREF(m); 
        return NULL;
    }
    Py_INCREF(&dihedralType);

    int result = PyModule_AddObject(m, "Dihedral", (PyObject*)&dihedralType);
    if (result < 0) {
        PyErr_Print();  // Print any Python exception
        Py_DECREF(&dihedralType);
        Py_DECREF(m);
        return NULL;
    }

    if (PyType_Ready(&znzType) < 0) {
        PyErr_Print();  // Print the actual error
        Py_DECREF(m); 
        return NULL;
    }
    Py_INCREF(&znzType);

    result = PyModule_AddObject(m, "ZNZ", (PyObject*)&znzType);
    if (result < 0) {
        PyErr_Print();  // Print any Python exception
        Py_DECREF(&znzType);
        Py_DECREF(m);
        return NULL;
    }
    
    if (PyType_Ready(&dihedral_matrixType) < 0) {
        PyErr_Print();  // Print the actual error
        Py_DECREF(m); 
        return NULL;
    }
    Py_INCREF(&dihedral_matrixType);

    result = PyModule_AddObject(m, "DihedralTensor", (PyObject*)&dihedral_matrixType);
    if (result < 0) {
        PyErr_Print();  // Print any Python exception
        Py_DECREF(&dihedral_matrixType);
        Py_DECREF(m);
        return NULL;
    }

    if (PyType_Ready(&symmetricType) < 0) {
        PyErr_Print();  // Print the actual error
        Py_DECREF(m); 
        return NULL;
    }
    Py_INCREF(&symmetricType);

    result = PyModule_AddObject(m, "Symmetric", (PyObject*)&symmetricType);
    if (result < 0) {
        PyErr_Print();  // Print any Python exception
        Py_DECREF(&symmetricType);
        Py_DECREF(m);
        return NULL;
    }



    return m; 
}  
  
   