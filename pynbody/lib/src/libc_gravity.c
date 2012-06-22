#include"Python.h"
#include"numpy/arrayobject.h"

#include"common.h"
#include"p2p_phi_kernel.h"
#include"p2p_acc_kernel.h"
#include"p2p_acc_jerk_kernel.h"
#include"p2p_tstep_kernel.h"
#include"p2p_pnacc_kernel.h"

//
// Python methods' interface
////////////////////////////////////////////////////////////////////////////////
static PyObject *
p2p_phi_kernel(PyObject *_self, PyObject *_args)
{
    return _p2p_phi_kernel(_args);
}


static PyObject *
p2p_acc_kernel(PyObject *_self, PyObject *_args)
{
    return _p2p_acc_kernel(_args);
}


static PyObject *
p2p_acc_jerk_kernel(PyObject *_self, PyObject *_args)
{
    return _p2p_acc_jerk_kernel(_args);
}


static PyObject *
p2p_tstep_kernel(PyObject *_self, PyObject *_args)
{
    return _p2p_tstep_kernel(_args);
}


static PyObject *
p2p_pnacc_kernel(PyObject *_self, PyObject *_args)
{
    return _p2p_pnacc_kernel(_args);
}


static PyMethodDef libc_gravity_meths[] = {
    {"p2p_phi_kernel", (PyCFunction)p2p_phi_kernel, METH_VARARGS,
                "returns the Newtonian gravitational potential."},
    {"p2p_acc_kernel", (PyCFunction)p2p_acc_kernel, METH_VARARGS,
                "returns the Newtonian gravitational acceleration."},
    {"p2p_acc_jerk_kernel", (PyCFunction)p2p_acc_jerk_kernel, METH_VARARGS,
                "returns the Newtonian gravitational acceleration and jerk."},
    {"p2p_tstep_kernel", (PyCFunction)p2p_tstep_kernel, METH_VARARGS,
                "returns the next time-step due to gravitational interaction."},
    {"p2p_pnacc_kernel", (PyCFunction)p2p_pnacc_kernel, METH_VARARGS,
                "returns the post-Newtonian gravitational acceleration."},
    {NULL, NULL, 0, NULL},
};


PyMODINIT_FUNC initlibc32_gravity(void)
{
    PyObject *ret;

    ret = Py_InitModule3("libc32_gravity", libc_gravity_meths,
                         "A extension module for Newtonian and post-Newtonian"
                         " gravity.");

    import_array();

    if (ret == NULL)
        return;
}


PyMODINIT_FUNC initlibc64_gravity(void)
{
    PyObject *ret;

    ret = Py_InitModule3("libc64_gravity", libc_gravity_meths,
                         "A extension module for Newtonian and post-Newtonian"
                         " gravity.");

    import_array();

    if (ret == NULL)
        return;
}

