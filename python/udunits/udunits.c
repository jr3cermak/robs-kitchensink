#include <Python.h>
#include <stdlib.h>
#include <udunits2.h>

/* Simple udunits wrapper to udunits2 C library */

static PyObject *
udunits(PyObject *self, PyObject *args) {

int retcode = 0;
const char *units_from;
const char *units_to;

ut_system*      unitSystem;
ut_unit*        sys1;
ut_unit*        sys2;
int             convertible;
cv_converter*   converter;
float           slope;
float           intercept;

/* Collect arguments from python */
if (!PyArg_ParseTuple(args, "ss", &units_from, &units_to))
    return NULL;

/* Return to python: 

  Format 1: [error_code, msg1, msg2]
  Format 2: [no_error, slope, intercept]

*/
PyObject *list = PyList_New(0);

    /* Initialize the unitSystem, after disabling error emissions */
    ut_set_error_message_handler(ut_ignore);
    unitSystem = ut_read_xml(NULL);

    sys1 = ut_parse(unitSystem, units_from, UT_ASCII);
    sys2 = ut_parse(unitSystem, units_to,   UT_ASCII);

    if (sys1 == NULL) {
      retcode = -1;
    }

    if (sys2 == NULL) {
      retcode = -2;
    }

    if (retcode == -1) { /* Unable to parse submitted from units from */
      PyList_Append(list, Py_BuildValue("i", retcode));
      PyList_Append(list, Py_BuildValue("s", "Unable to parse from"));
      PyList_Append(list, Py_BuildValue("s", units_from));
    }

    if (retcode == -2) { /* Unable to parse submitted from units from */
      PyList_Append(list, Py_BuildValue("i", retcode));
      PyList_Append(list, Py_BuildValue("s", "Unable to parse to"));
      PyList_Append(list, Py_BuildValue("s", units_to));
    }

    /* Are sys1 and sys2 convertible? */
    convertible = ut_are_convertible(sys1, sys2);

    if (convertible == 0) {
      retcode = -3;
      PyList_Append(list, Py_BuildValue("i", retcode));
      PyList_Append(list, Py_BuildValue("s", "Conversion not possible"));
      return list;
    }

    /* Do the conversion */
    converter = ut_get_converter(sys1, sys2);

    /* Conversion failed for another reason */
    if (converter == NULL) {
      retcode = -4;
      PyList_Append(list, Py_BuildValue("i", retcode));
      PyList_Append(list, Py_BuildValue("s", "Conversion failed"));
      return list;
    }

    /* FINAL CONVERSION */
    PyList_Append(list, Py_BuildValue("i", retcode));

    /* Get intercept */
    intercept = cv_convert_float(converter, 0.0);

    /* Get slope */
    slope = cv_convert_float(converter, 1.0) - intercept;

    PyList_Append(list, Py_BuildValue("d", slope));
    PyList_Append(list, Py_BuildValue("d", intercept));

    /* Free converter object */
    ut_free(sys1);
    ut_free(sys2);
    cv_free(converter);

    /* Return the list to python */
    return list;
}

PyMethodDef methods[] = {
    {"udunits", udunits, METH_VARARGS, "Returns conversion for specified units"},
    {NULL, NULL, 0, NULL}
};

PyMODINIT_FUNC
initudunits()
{
    (void) Py_InitModule("udunits", methods);
}
